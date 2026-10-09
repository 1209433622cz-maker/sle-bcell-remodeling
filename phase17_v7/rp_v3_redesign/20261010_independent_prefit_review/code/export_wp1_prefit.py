#!/usr/bin/env python3
"""Export WP1 sufficient count objects on the original local project.

This program NEVER fits a disease coefficient or a bootstrap. It does NOT choose
between score-first and expression-first A1 standardization. It verifies the
frozen files, maps A2 to A0 without reading disease metadata, reconstructs A1
support, and exports raw IFN sums with their *full* library totals. These permit
later inference only after the pre-effect estimand review has been resolved.

Dependencies: Python >=3.9; numpy, pandas, scipy, h5py. Output must be new.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from scipy import sparse

RAW_REL='phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad'
A0_REL='phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad'
DESIGN_REL='phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/06_primary_bconv_model_matrix.csv'
STAGE_REL='phase17_v7/rp_v3_redesign/20261009_stage0b'
EXPECTED={RAW_REL:'DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5',
 A0_REL:'594A040FC483973B38B744D5D0E526633D7F1C91F2544D34C28D35F2084E3AFB',
 DESIGN_REL:'E3CDB2B7038712534D032FF008F7386976BF63EDCD3E07589EE0C97CC3295876'}
A2_HASH='4943C575EB010572FA874864FD8258624310E077D5AF439EDA0C446C1A1B5F59'


def digest(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest().upper()


def vector(node):
    if isinstance(node,h5py.Group):
        if not {'codes','categories'}<=set(node):raise ValueError('Unsupported categorical '+node.name)
        code=node['codes'][:]
        if (code<0).any():raise ValueError('Missing categorical values '+node.name)
        return vector(node['categories'])[code]
    return node.asstr()[:] if h5py.check_string_dtype(node.dtype) else node[:]


def align_index(reference, other):
    r=pd.Index(reference);o=pd.Index(other)
    if not r.is_unique or not o.is_unique:raise ValueError('Nonunique source_cell_index')
    if len(r)!=len(o):raise ValueError('Cell universe sizes differ')
    idx=o.get_indexer(r)
    if (idx<0).any():raise ValueError('Cell universes differ')
    return idx


def overlap_map(a0_cluster, a2_cluster):
    """Majority *broad-compartment* cell overlap; ties are an unresolved mapping."""
    a0=np.asarray(a0_cluster).astype(str);a2=np.asarray(a2_cluster).astype(str)
    if set(a0)-{'0','1','2','3','4'}:raise ValueError('Unexpected A0 labels')
    broad=np.where(a0=='3','B_ASC','B_CONV')
    table=pd.crosstab(pd.Series(a2,name='A2_cluster'),pd.Series(broad,name='A0_broad')).reindex(columns=['B_CONV','B_ASC'],fill_value=0)
    if (table.B_CONV==table.B_ASC).any():raise ValueError('A2 overlap tie; no effect-based tie breaking allowed')
    rows=[];mapping={}
    for label,row in table.iterrows():
        choice='B_CONV' if row.B_CONV>row.B_ASC else 'B_ASC';mapping[str(label)]=choice
        rows.append({'A2_cluster':str(label),'overlap_B_CONV':int(row.B_CONV),'overlap_B_ASC':int(row.B_ASC),
                     'mapped_A0_broad':choice,'cluster_purity_vs_A0':float(row[choice]/row.sum())})
    mapped=np.asarray([mapping[c] for c in a2])
    if set(mapped)!={'B_CONV','B_ASC'}:raise ValueError('Broad mapping loses a compartment; requires explicit review')
    confusion=pd.crosstab(pd.Series(broad,name='A0_broad'),pd.Series(mapped,name='A2_mapped'))
    # Purity/recall against A0 are reference concordance, NOT external biological accuracy.
    return broad,mapped,pd.DataFrame(rows),confusion


def selected_counts_and_totals(h, genes, block_size=2048):
    """Sum duplicate symbols; compute denominators from every original feature."""
    symbols=vector(h['var/feature_name']).astype(str)
    x=h['X'];enc=x.attrs.get('encoding-type','');enc=enc.decode() if isinstance(enc,bytes) else enc
    if enc!='csr_matrix':raise ValueError('Raw X must be CSR for this streaming exporter; do not guess a different slot')
    n,m=map(int,x.attrs['shape'])
    if m!=len(symbols):raise ValueError('Raw variable alignment failure')
    selector_rows=[];selector_cols=[]
    for j,g in enumerate(genes):
        ix=np.flatnonzero(symbols==g)
        if not len(ix):raise ValueError('Missing source gene '+g)
        selector_rows.extend(ix.tolist());selector_cols.extend([j]*len(ix))
    select=sparse.csr_matrix((np.ones(len(selector_rows),dtype=np.int64),(selector_rows,selector_cols)),shape=(m,len(genes)))
    ptr=x['indptr'][:];out=np.zeros((n,len(genes)),dtype=np.int64);tot=np.zeros(n,dtype=np.int64)
    for lo in range(0,n,block_size):
        hi=min(lo+block_size,n);p0=int(ptr[lo]);p1=int(ptr[hi])
        data=x['data'][p0:p1]
        if not np.isfinite(data).all() or (data<0).any() or not np.equal(data,np.rint(data)).all():
            raise ValueError('Raw X is not nonnegative integer counts')
        block=sparse.csr_matrix((data.astype(np.int64),x['indices'][p0:p1],ptr[lo:hi+1]-p0),shape=(hi-lo,m))
        tot[lo:hi]=np.asarray(block.sum(axis=1)).ravel()
        out[lo:hi]=(block@select).toarray()
    if (tot<=0).any():raise ValueError('Zero full-library totals')
    return out,tot


def axis_scores(counts,totals,params):
    means=params.mean_log1p_cp10k.to_numpy(float);sd=params.population_sd_log1p_cp10k.to_numpy(float)
    signs=params.sign.to_numpy(int)
    if not np.isfinite(sd).all() or (sd<=0).any():raise ValueError('Invalid frozen A1 SD')
    x=np.log1p(counts.astype(float)*10000/totals[:,None]);z=(x-means)/sd
    return z[:,signs==1].mean(axis=1)-z[:,signs==-1].mean(axis=1),x


def t0_log(counts,totals):
    if (np.asarray(totals)<=0).any():raise ValueError('Zero pseudobulk total')
    return np.log2(np.asarray(counts)*1e6/np.asarray(totals)[:,None]+0.5)


def aggregate(counts,totals,codes,n_groups):
    codes=np.asarray(codes);valid=codes>=0
    output=np.zeros((n_groups,counts.shape[1]),dtype=np.int64)
    denominator=np.zeros(n_groups,dtype=np.int64)
    number=np.zeros(n_groups,dtype=np.int64)
    np.add.at(output,codes[valid],counts[valid]);np.add.at(denominator,codes[valid],totals[valid]);np.add.at(number,codes[valid],1)
    return output,denominator,number


def matrix_rank_elimination(values, tolerance=1e-10):
    """Return matrix rank without invoking the unstable Windows LAPACK SVD."""
    a=np.asarray(values,dtype=float).copy()
    if a.ndim!=2 or not np.isfinite(a).all():raise ValueError('Invalid design matrix')
    rank=0
    for column in range(a.shape[1]):
        pivot=rank+int(np.argmax(np.abs(a[rank:,column]))) if rank<a.shape[0] else rank
        if rank>=a.shape[0] or abs(a[pivot,column])<=tolerance:continue
        a[[rank,pivot]]=a[[pivot,rank]]
        a[rank]/=a[rank,column]
        for row in range(a.shape[0]):
            if row!=rank:a[row]-=a[row,column]*a[rank]
        rank+=1
        if rank==a.shape[0]:break
    return rank


def do_export(root:Path,stage:Path,out:Path,validate_only=False):
    if out.exists():raise FileExistsError('Use a new output directory: '+str(out))
    out.mkdir(parents=True);receipts=[]
    try:
        required=[(root/k,v) for k,v in EXPECTED.items()]+[(stage/'a2_rebuild/08_isg_excluded_representation.h5ad',A2_HASH)]
        for p,expected in required:
            exists=p.is_file();actual=digest(p) if exists else ''
            receipts.append({'file':str(p),'present':exists,'expected_sha256':expected,'actual_sha256':actual,'pass':exists and expected==actual})
        pd.DataFrame(receipts).to_csv(out/'input_receipts.csv',index=False)
        if not all(r['pass'] for r in receipts):raise ValueError('Required source absent or SHA256 mismatch; no inference permitted')
        for r in pd.read_csv(stage/'15_STAGE0B_INTEGRITY_MANIFEST.csv').to_dict('records'):
            p=stage/str(r['file']).replace('\\','/')
            if not p.is_file() or p.stat().st_size!=r['size_bytes'] or digest(p)!=r['sha256']:
                raise ValueError('Final Stage0B manifest mismatch: '+str(p))
        if validate_only:
            (out/'STATUS.json').write_text(json.dumps({'status':'INPUT_HASH_CHECK_PASS_ONLY','disease_coefficients_fitted':False},indent=2))
            return
        # No disease design file is parsed before mapping and its receipt are written.
        with h5py.File(root/RAW_REL,'r') as raw,h5py.File(root/A0_REL,'r') as a0,h5py.File(required[-1][0],'r') as a2:
            src=vector(raw['obs/source_cell_index'])
            i0=align_index(src,vector(a0['obs/source_cell_index']));i2=align_index(src,vector(a2['obs/source_cell_index']))
            for key in ('donor_id','sample_uuid','library_uuid','Processing_Cohort'):
                a=vector(raw['obs/'+key]).astype(str)
                if not np.array_equal(a,vector(a0['obs/'+key])[i0].astype(str)) or not np.array_equal(a,vector(a2['obs/'+key])[i2].astype(str)):
                    raise ValueError('Technical metadata alignment failure '+key)
            broad,mapped,map_table,confusion=overlap_map(vector(a0['obs/leiden_harmony_r0_4'])[i0],vector(a2['obs/leiden_harmony_r0_4'])[i2])
            map_table.to_csv(out/'A2_to_A0_overlap_mapping.csv',index=False);confusion.to_csv(out/'A2_to_A0_reference_confusion.csv')
            (out/'A2_MAPPING_LOCK.json').write_text(json.dumps({'mapping_sha256':digest(out/'A2_to_A0_overlap_mapping.csv'),
                'created_at':datetime.now(timezone.utc).isoformat(),'disease_design_parsed':False,
                'rule':'unique-majority broad-compartment cell overlap; ties/compartment collapse stop',
                'not_biological_ground_truth':True},indent=2))
            par=pd.read_csv(stage/'07_A1_FROZEN_STANDARDIZATION_PARAMETERS.csv');contract=json.loads((stage/'04_SCORE_CONTRACTS.json').read_text())
            ifn=contract['program_members'];markers=list(par.gene_symbol)
            if set(ifn)&set(markers):raise ValueError('Unexpected frozen program/marker overlap')
            gene_order=ifn+markers
            counts,totals=selected_counts_and_totals(raw,gene_order)
            score,x=axis_scores(counts[:,len(ifn):],totals,par)
            if not np.allclose(x.mean(axis=0),par.mean_log1p_cp10k,rtol=0,atol=1e-6) or not np.allclose(x.std(axis=0,ddof=0),par.population_sd_log1p_cp10k,rtol=0,atol=1e-6):
                raise ValueError('A1 raw-count normalization does not reproduce frozen moments; do not replace frozen parameters')
            summary=json.loads((stage/'07_A1_SCORE_TECHNICAL_SUMMARY.json').read_text())
            cuts=np.array([summary['quantile_thresholds'][k] for k in ['q20','q40','q60','q80']])
            if not np.allclose(np.quantile(score[broad=='B_CONV'],[.2,.4,.6,.8]),cuts,rtol=0,atol=1e-6):
                raise ValueError('Frozen A1 cutpoints not reproduced')
            bins=np.searchsorted(cuts,score,side='left')+1
            meta=pd.DataFrame({'source_cell_index':src,'donor_id':vector(raw['obs/donor_id']).astype(str),
                'sample_uuid':vector(raw['obs/sample_uuid']).astype(str),
                'cohort':pd.to_numeric(vector(raw['obs/Processing_Cohort'])).astype(int),
                'A0_broad':broad,'A2_broad':mapped,'A1_bin':bins,'A1_score':score})
            meta['stratum_id']=meta.sample_uuid+'__C'+meta.cohort.astype(str)
        # Mapping is now locked. The existing design is used only for technical support/T0-reference checks.
        design=pd.read_csv(root/DESIGN_REL,dtype={'donor_id':str})
        if len(design)!=89 or design.stratum_id.nunique()!=89 or design.donor_id.nunique()!=89:raise ValueError('Unexpected primary unit registry')
        stratum_order=pd.Index(design.stratum_id);row=stratum_order.get_indexer(meta.stratum_id)
        prior=meta.loc[row>=0,['stratum_id','donor_id']].drop_duplicates().merge(design[['stratum_id','donor_id']],on='stratum_id',suffixes=('_cell','_design'),validate='one_to_one')
        if len(prior)!=89 or not prior.donor_id_cell.eq(prior.donor_id_design).all():raise ValueError('Design-donor ID mismatch')
        a0codes=np.where((row>=0)&(broad=='B_CONV'),row,-1)
        a2codes=np.where((row>=0)&(mapped=='B_CONV'),row,-1)
        a1codes=np.where(a0codes>=0,row*5+bins-1,-1)
        blocks={}
        for name,codes,size in [('A0',a0codes,89),('A2',a2codes,89),('A1_bin',a1codes,445)]:
            c,t,n=aggregate(counts[:,:12],totals,codes,size);blocks[name]=(c,t,n)
            if name=='A1_bin':
                frame=pd.DataFrame({'stratum_id':np.repeat(design.stratum_id.to_numpy(),5),'donor_id':np.repeat(design.donor_id.to_numpy(),5),'A1_bin':np.tile(np.arange(1,6),89)})
            else:frame=design[['stratum_id','donor_id']].copy()
            frame['cell_count']=n;frame['full_raw_library_total']=t
            for j,g in enumerate(ifn):frame['raw_IFN_'+g]=c[:,j]
            frame.to_csv(out/(name+'_sufficient_raw_counts.csv'),index=False)
        if not np.array_equal(blocks['A0'][2],design.bconv_cells.to_numpy()):raise ValueError('Original A0 cell counts mismatch')
        if not np.array_equal(blocks['A0'][1],design.bconv_library_size_umi.to_numpy()):raise ValueError('Original A0 full-library totals mismatch')
        old=pd.read_csv(stage/'08_A1_DONOR_BIN_SUPPORT.csv',dtype={'donor_id':str}).sort_values(['stratum_index_local','a1_bin'])
        if not np.array_equal(blocks['A1_bin'][2],old.cell_count.to_numpy()):raise ValueError('A1 bin counts do not match Stage0B; do not change cutpoints')
        ref=pd.read_csv(stage/'11_T0_FROZEN_REFERENCE_PARAMETERS.csv');normal=design.is_managed.eq(0).to_numpy()
        if normal.sum()!=43:raise ValueError('T0 reference is not the frozen 43 controls')
        log=t0_log(blocks['A0'][0],blocks['A0'][1]);mu=log[normal].mean(axis=0);sd=log[normal].std(axis=0,ddof=0)
        if not np.allclose(mu,ref.control_mean_log2_cpm_plus_0_5,rtol=0,atol=1e-6) or not np.allclose(sd,ref.control_population_sd_log2_cpm_plus_0_5,rtol=0,atol=1e-6):
            raise ValueError('T0 reference not reproduced from full raw background; no branch restandardization allowed')
        support=design[['stratum_id','donor_id','is_managed']].copy()
        support['A0_ge50']=blocks['A0'][2]>=50;support['A1_all_five_ge30']=(blocks['A1_bin'][2].reshape(89,5)>=30).all(axis=1)
        support['A2_ge50_diagnostic']=blocks['A2'][2]>=50
        support['candidate_common_if_A2_ge50_adopted']=support[['A0_ge50','A1_all_five_ge30','A2_ge50_diagnostic']].all(axis=1)
        support.to_csv(out/'candidate_joint_support.csv',index=False)
        # Preserve the frozen primary-base design from Gate C4B. The two
        # ethnicity indicators are complements in this cohort and must not be
        # entered together with an intercept.
        covariates=['intercept','is_managed','age_centered','ethnicity_asian']
        keep=support.candidate_common_if_A2_ge50_adopted.to_numpy()
        support_report={'n_original_strata':len(design),'n_A1_complete':int(support.A1_all_five_ge30.sum()),
            'n_candidate_joint':int(keep.sum()),
            'candidate_joint_donors_by_is_managed':{str(k):int(v) for k,v in support.loc[keep].groupby('is_managed').donor_id.nunique().items()},
            'candidate_joint_design_rank':matrix_rank_elimination(design.loc[keep,covariates].to_numpy(float)) if keep.any() else 0,
            'required_design_columns':covariates,'T0_reference_kept_at_43':True,
            'status':'SUPPORT_DIAGNOSTICS_ONLY_NOT_G1_OR_WP1_ADJUDICATION'}
        (out/'candidate_support_diagnostics.json').write_text(json.dumps(support_report,indent=2))
        # Technical covariates are copied unchanged; no centering or refit occurs here.
        design[['stratum_id','donor_id','intercept','age_centered','ethnicity_asian','ethnicity_european','is_managed']].to_csv(out/'primary_design_fixed.csv',index=False)
        meta.to_csv(out/'cell_mapping_and_A1_axis.csv.gz',index=False,compression='gzip')
        for f in ['04_SCORE_CONTRACTS.json','07_A1_FROZEN_STANDARDIZATION_PARAMETERS.csv','11_T0_FROZEN_REFERENCE_PARAMETERS.csv','09_PI_REF.csv','17_WP1_ANNOTATION_SENSITIVITY_EXECUTION_CONTRACT.md']:
            shutil.copy2(stage/f,out/f)
        (out/'STATUS.json').write_text(json.dumps({'status':'PREFIT_EXPORT_COMPLETE_REVIEW_REQUIRED',
            'disease_coefficients_fitted':False,'bootstrap_replicates':0,
            'A1_operator_selected':False,'A1_weighted_score_not_automatically_RPv3_beta_S':True,
            'full_IFN_exclusion_claim':False,'A2_retains_program_gene':'LY6E',
            'WP4':'HOLD_CONDITIONAL','SUBMISSION':'HOLD',
            'scope':'No regression; no manuscript/figure changes; no replacement of frozen contracts'},indent=2))
        pd.DataFrame([{'relative_path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(out.iterdir()) if p.is_file()]).to_csv(out/'SHA256SUMS.csv',index=False)
        zp=out.with_suffix('.zip')
        if zp.exists():raise FileExistsError(zp)
        with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.iterdir()):
                if p.is_file():z.write(p,p.name)
        print('PREFIT EXPORT ONLY:',zp)
    except Exception as e:
        (out/'EXPORT_HOLD.json').write_text(json.dumps({'status':'HOLD_PREFIT_EXPORT','reason':str(e),
            'disease_coefficients_fitted':False,'partial_outputs':'diagnostic only; not inference inputs'},indent=2))
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True);p.add_argument('--stage0b',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--validate-only',action='store_true')
    a=p.parse_args()
    try:do_export(a.project_root,a.stage0b or a.project_root/STAGE_REL,a.output,a.validate_only)
    except Exception as exc:print('HOLD:',exc,file=sys.stderr);sys.exit(2)
