#!/usr/bin/env python3
"""Read-only, outcome-free audit of the received RP-v3 Stage 0B archive.

No disease coefficient, branch score association, p value or bootstrap is fitted.
Original contracts are never rewritten. Input-manifest self references are diagnosed,
not 'fixed' by changing their historical bytes.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path, PureWindowsPath
import h5py
import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest().upper()


def read_vector(node):
    if isinstance(node, h5py.Group):
        if not {'categories', 'codes'} <= set(node):
            raise ValueError(f'Unsupported HDF5 vector: {node.name}')
        cat = read_vector(node['categories'])
        codes = np.asarray(node['codes'][:], dtype=int)
        if (codes < 0).any():
            raise ValueError(f'Missing category in {node.name}')
        return cat[codes]
    if h5py.check_string_dtype(node.dtype):
        return node.asstr()[:]
    return node[:]


def resolve_stage_path(stage: Path, raw: str) -> Path | None:
    # Resolve both stage-relative members and root-qualified aliases of this stage.
    text = str(raw).replace('\\', '/')
    marker = stage.name + '/'
    if marker in text:
        text = text.split(marker, 1)[1]
    elif text.startswith('phase17_v7/'):
        return None  # external project input, not a relative archive member
    p = (stage / text).resolve()
    if not p.is_relative_to(stage.resolve()):
        raise ValueError(f'Unsafe manifest path: {raw}')
    return p


def audit(stage: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError(f'Use a fresh output directory: {output}')
    output.mkdir(parents=True)
    checks = []
    def check(name, ok, evidence):
        checks.append({'check': name, 'pass': bool(ok), 'evidence': str(evidence)})
    def load(name):
        return json.loads((stage / name).read_text(encoding='utf-8-sig'))

    inventory = []
    for name in ('15_STAGE0B_INTEGRITY_MANIFEST.csv', '01_STAGE0B_INPUT_AND_CONTRACT_MANIFEST.csv'):
        for row in pd.read_csv(stage / name).to_dict('records'):
            p = resolve_stage_path(stage, row['file'])
            exists = p is not None and p.is_file()
            digest = sha256(p) if exists else ''
            size = p.stat().st_size if exists else None
            status = ('PASS' if exists and digest == row['sha256'] and size == row['size_bytes']
                      else 'MISMATCH' if exists else 'EXTERNAL_INPUT_NOT_BUNDLED')
            inventory.append(dict(manifest=name, file=row['file'], expected_sha256=row['sha256'],
                                  observed_sha256=digest, expected_bytes=row['size_bytes'],
                                  observed_bytes=size, status=status))
    manifest = pd.DataFrame(inventory)
    manifest.to_csv(output / 'manifest_verification.csv', index=False)
    final = manifest[manifest.manifest.str.startswith('15_')]
    older = manifest[manifest.manifest.str.startswith('01_')]
    check('Final_manifest_all_31_members_match', len(final)==31 and final.status.eq('PASS').all(),
          final.status.value_counts().to_dict())
    # A failing check records an actual audit finding; it is never suppressed.
    check('Earlier_input_manifest_current_local_entries_match',
          not older.status.eq('MISMATCH').any(), older.status.value_counts().to_dict())

    a1 = pd.read_csv(stage / '02_A1_CONTINUOUS_AXIS_DICTIONARY.csv')
    par = pd.read_csv(stage / '07_A1_FROZEN_STANDARDIZATION_PARAMETERS.csv')
    score = load('04_SCORE_CONTRACTS.json')
    genes = score['program_members']
    feat = pd.read_csv(stage / '03_A2_FROZEN_FEATURES.csv')
    overlaps = sorted(set(feat.feature_name) & set(genes))
    pd.DataFrame({'IFN_program_gene': genes,
                  'in_A1_dictionary': [g in set(a1.gene_symbol) for g in genes],
                  'in_A2_features': [g in set(feat.feature_name) for g in genes]}).to_csv(
                      output / 'identity_IFN_overlap_audit.csv', index=False)
    check('A1_has_14_unique_markers', a1.gene_symbol.nunique()==14 and len(a1)==14, len(a1))
    check('A1_signs_7_positive_7_negative', (a1.sign==1).sum()==7 and (a1.sign==-1).sum()==7,
          a1.sign.value_counts().to_dict())
    check('A1_has_no_literal_IFN12_overlap', not set(a1.gene_symbol)&set(genes),
          sorted(set(a1.gene_symbol)&set(genes)))
    check('A1_parameters_match_dictionary', list(par.gene_symbol)==list(a1.gene_symbol)
          and list(par.sign)==list(a1.sign), 'exact ordered marker/sign equality')
    check('A1_frozen_SDs_positive_finite', np.isfinite(par.iloc[:,2:].values).all()
          and (par.population_sd_log1p_cp10k>0).all(), par.population_sd_log1p_cp10k.min())
    check('A2_has_3000_frozen_features', len(feat)==3000 and feat.var_name.nunique()==3000, len(feat))
    check('A2_strong_ISG_flags_zero', not feat.is_strong_isg.any(), int(feat.is_strong_isg.sum()))
    check('A2_immunoglobulin_flags_zero', not feat.is_immunoglobulin.any(), int(feat.is_immunoglobulin.sum()))
    # Broader claim test: this is NOT the historical strong-ISG contract criterion.
    check('A2_full_IFN12_exclusion_claim_supported', not overlaps,
          'Not a frozen strong-ISG gate. Literal retained program members: '+','.join(overlaps))

    with h5py.File(stage/'a2_rebuild/03_a2_prepared.h5ad','r') as a, \
         h5py.File(stage/'a2_rebuild/08_isg_excluded_representation.h5ad','r') as b:
        shape=tuple(int(x) for x in a['X'].attrs['shape'])
        check('Prepared_shape_150402_3000', shape==(150402,3000), shape)
        ids=read_vector(b['obs/cell_id'])
        check('A2_unique_cell_IDs_150402', len(ids)==150402 and len(set(ids))==150402, len(ids))
        check('Prepared_final_cell_order_identical', np.array_equal(ids,read_vector(a['obs/cell_id'])),
              'prepared/final cell_id order')
        check('A2_frozen_feature_order_exact',np.array_equal(read_vector(b['var/gene_id_index']),feat.var_name.to_numpy()),
              'HDF5 gene_id_index vs frozen CSV var_name')
        labels=read_vector(b['obs/leiden_harmony_r0_4'])
        counts=pd.Series(labels).value_counts().sort_index()
        saved=pd.read_csv(stage/'10_A2_CLUSTER_COVERAGE.csv')
        counts.rename_axis('A2_cluster').reset_index(name='cell_count').to_csv(output/'A2_cluster_count_recount.csv',index=False)
        check('A2_five_clusters',len(counts)==5,counts.to_dict())
        for key in ['X_pca','X_pca_harmony']:
            arr=b['obsm'][key][:]
            check('A2_'+key+'_shape_and_finiteness',arr.shape==(150402,50) and np.isfinite(arr).all(),arr.shape)
        columns=list(b['obs'].keys())
        forbidden={'disease','disease_state','is_managed','is_flare','case_control','treatment'}
        check('A2_checkpoint_has_no_explicit_outcome_columns',not forbidden&set(columns),columns)
        check('A2_stored_disease_blind_flag',bool(b['uns/phase17_c2b2_branch/disease_blind'][()]),
              'Metadata/column check only; not a complete source-code proof of blinding')
        check('Prepared_nonnegative_finite_expression',np.isfinite(a['X/data'][:]).all()
              and (a['X/data'][:]>=0).all(),'prepared normalized X, not raw IFN counts')
        checkpoint_info={'canonical_prepared_X_shape':shape,'canonical_final_has_X':'X' in b,
                         'canonical_final_layers':list(b['layers'].keys()),'obs_columns':columns}

    support=pd.read_csv(stage/'08_A1_DONOR_BIN_SUPPORT.csv',dtype={'donor_id':str})
    check('A1_support_unique_stratum_bin',not support.duplicated(['stratum_id','a1_bin']).any(),len(support))
    check('A1_support_counts_nonnegative_integers', (support.cell_count>=0).all()
          and (support.cell_count%1==0).all(),support.cell_count.min())
    check('A1_support_flags_match_30_rule',np.array_equal(support.meets_cell_threshold,support.cell_count>=30), '>=30')
    p=support.pivot(index=['stratum_id','donor_id'],columns='a1_bin',values='cell_count').sort_index(axis=1)
    check('A1_support_89_units_5_bins',p.shape==(89,5) and not p.isna().any().any(),p.shape)
    check('A1_primary_units_are_89_distinct_donors',support.donor_id.nunique()==89, support.donor_id.nunique())
    q=p.copy();q['all_5_bins_ge30']=(p>=30).all(axis=1)
    q['failing_bins']=[';'.join(str(int(k)) for k,v in zip(p.columns,vals) if v<30) for vals in p.values]
    q.to_csv(output/'A1_complete_support_membership.csv')
    summary=pd.read_csv(stage/'08_A1_BIN_SUPPORT_SUMMARY.csv').set_index('a1_bin')
    marginal=(p>=30).sum()
    check('A1_marginal_support_reproduced',np.array_equal(marginal.values,summary.supported_strata.values),marginal.to_dict())
    check('A1_marginal_arm_counts_sum',np.array_equal(summary.normal_donors+summary.managed_donors,summary.supported_donors),
          'Only summary arithmetic; individual disease labels not used')
    pi=pd.read_csv(stage/'09_PI_REF.csv')
    pi_recalc=pi.normal_control_cells_in_supported_donor_bins / pi.normal_control_cells_in_supported_donor_bins.sum()
    check('Pi_arithmetic_matches_own_count_column',np.allclose(pi_recalc,pi.pi_ref,rtol=0,atol=1e-12),float(abs(pi_recalc-pi.pi_ref).max()))
    check('Pi_all_five_weights_positive_sum_one',(pi.pi_ref>0).all() and abs(pi.pi_ref.sum()-1)<1e-12,pi.pi_ref.sum())
    t0=pd.read_csv(stage/'11_T0_FROZEN_REFERENCE_PARAMETERS.csv')
    check('T0_ordered_IFN12_and_43_reference',list(t0.gene_symbol)==genes and t0.reference_strata.eq(43).all(),len(t0))
    check('T0_SDs_positive_finite',np.isfinite(t0.iloc[:,1:].values).all()
          and (t0.control_population_sd_log2_cpm_plus_0_5>0).all(), t0.control_population_sd_log2_cpm_plus_0_5.min())
    sim=pd.read_csv(stage/'13_SIMULATION_TECHNICAL_RESULTS.csv')
    check('Simulation_summary_five_scenarios_25_rows',sim.scenario.nunique()==5 and len(sim)==25, len(sim))
    check('Simulation_summary_400_replicates_per_row',sim.replicates.eq(400).all(), sorted(sim.replicates.unique()))
    check('Simulation_summary_no_reported_fit_failure',sim.fit_failure_rate.eq(0).all(),sim.fit_failure_rate.max())
    check('Simulation_bias_arithmetic',np.allclose(sim.mean_estimate-sim.truth,sim.bias,atol=1e-12,rtol=0),
          float(abs(sim.mean_estimate-sim.truth-sim.bias).max()))
    check('Simulation_RMSE_at_least_abs_bias',(sim.rmse+1e-12>=abs(sim.bias)).all(),sim.rmse.min())
    check('Simulation_coverage_valid_400_trial_counts',(sim.empirical_95pct_coverage.between(0,1)).all()
          and np.allclose(sim.empirical_95pct_coverage*400,np.round(sim.empirical_95pct_coverage*400)),
          [sim.empirical_95pct_coverage.min(),sim.empirical_95pct_coverage.max()])
    pd.DataFrame(checks).to_csv(output/'independent_checks.csv',index=False)
    result={
        'audit_date':'2026-10-10','status':'WP1_PRE_EFFECT_REVIEW_REQUIRED',
        'received_G0':'PASS_G0','received_G1':'PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY',
        'independent_scope':'archive bytes, checkpoint structure, frozen tables, joint support; no disease effects',
        'final_manifest':final.status.value_counts().to_dict(),
        'earlier_manifest':older.status.value_counts().to_dict(),
        'checks_pass':sum(x['pass'] for x in checks),'checks_total':len(checks),
        'findings':[x for x in checks if not x['pass']],
        'A1_primary_strata':89,'A1_distinct_donors':89,
        'A1_marginal_support':{str(k):int(v) for k,v in marginal.items()},
        'A1_all_five_bins_supported':int(q.all_5_bins_ge30.sum()),
        'A1_any_bin_unsupported':int((~q.all_5_bins_ge30).sum()),
        'common_support_interpretation':'68 is an upper bound before applying A2 eligibility; group counts require ID-linked design',
        'A2_program_overlap':overlaps,'checkpoint_info':checkpoint_info,
        'simulation_summary_max_abs_bias':float(abs(sim.bias).max()),
        'simulation_summary_coverage_range':[float(sim.empirical_95pct_coverage.min()),float(sim.empirical_95pct_coverage.max())],
        'G2':'NOT_ASSESSED_FULL_PROTOCOL_PENDING','WP4':'HOLD_CONDITIONAL','SUBMISSION':'HOLD',
        'disease_coefficients_fitted':False,'bootstrap_replicates_run':0,
        'original_six_tests_rerun':False,
        'source_rebuild_verified':False,
        'missing_portable_inputs':['discovery raw-count H5AD','A0 cell-level reference H5AD',
            'Stage0B source builder / six tests'],
        'source_control_scope':'Original source bytes unchanged; source-coded provenance not inferred from summary flags.'}
    (output/'independent_status.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage0b',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(audit(a.stage0b,a.output),indent=2,ensure_ascii=False))
