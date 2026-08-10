#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, os
from pathlib import Path
from typing import Any

def decode(x: Any) -> str:
    return x.decode("utf-8", errors="replace") if isinstance(x, bytes) else str(x)

def read_vec(group, key):
    import numpy as np
    obj = group[key]
    if hasattr(obj, "keys") and "codes" in obj and "categories" in obj:
        codes = obj["codes"][:]; cats = [decode(x) for x in obj["categories"][:]]
        return np.array([cats[int(i)] if 0 <= int(i) < len(cats) else "" for i in codes], dtype=object)
    return np.array([decode(x) for x in obj[:]], dtype=object)

def read_genes(var):
    candidates = ["feature_name","gene_name","gene_symbol","symbol",decode(var.attrs.get("_index","_index")),"_index"]
    for key in dict.fromkeys(candidates):
        if key and key in var:
            return read_vec(var,key), key
    raise RuntimeError(f"No readable gene names in raw/var; keys={list(var.keys())}")

def resolve(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else root / value.replace("\\",os.sep).replace("/",os.sep)

def limits(values, m=3.0, floor=None, ceiling=None):
    import numpy as np
    v=np.asarray(values,float); v=v[np.isfinite(v)]
    med=float(np.median(v)); mad=float(np.median(np.abs(v-med))); s=1.4826*mad
    lo,hi=med-m*s,med+m*s
    if floor is not None: lo=max(lo,floor)
    if ceiling is not None: hi=min(hi,ceiling)
    return med,mad,lo,hi

def summary(df, group, metrics):
    def q01(x): return x.quantile(.01)
    def q05(x): return x.quantile(.05)
    def q95(x): return x.quantile(.95)
    def q99(x): return x.quantile(.99)
    x=df.groupby(group,observed=True)[metrics].agg(["count","min","median","mean","max",q01,q05,q95,q99])
    x.columns=[f"{a}_{b}" for a,b in x.columns]
    return x.reset_index()

def thresholds(df, group, m):
    import numpy as np, pandas as pd
    rows=[]
    for key,s in df.groupby(group,observed=True):
        cm,ca,cl,ch=limits(np.log10(s.n_counts+1),m)
        gm,ga,gl,gh=limits(np.log10(s.n_genes+1),m)
        mm,ma,_,mh=limits(s.pct_mito,m,0,100)
        hm,ha,_,hh=limits(s.pct_hb,m,0,100)
        pm,pa,_,ph=limits(s.pct_platelet,m,0,100)
        bm,ba,bl,_=limits(s.n_blineage_markers_detected,m,0,None)
        flag=(np.log10(s.n_counts+1)<cl)|(np.log10(s.n_counts+1)>ch)|(np.log10(s.n_genes+1)<gl)|(np.log10(s.n_genes+1)>gh)|(s.pct_mito>mh)|(s.pct_hb>hh)|(s.pct_platelet>ph)|(s.n_blineage_markers_detected<bl)
        rows.append({group:key,"n_cells":len(s),"log10_counts_median":cm,"log10_counts_mad":ca,"log10_counts_low_candidate":cl,"log10_counts_high_candidate":ch,"log10_genes_median":gm,"log10_genes_mad":ga,"log10_genes_low_candidate":gl,"log10_genes_high_candidate":gh,"pct_mito_median":mm,"pct_mito_mad":ma,"pct_mito_high_candidate":mh,"pct_hb_high_candidate":hh,"pct_platelet_high_candidate":ph,"blineage_markers_low_candidate":bl,"candidate_flagged_cells":int(flag.sum()),"candidate_flagged_fraction":float(flag.mean())})
    return pd.DataFrame(rows)

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",required=True)
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--discovery",default=r"Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad")
    ap.add_argument("--chunk-rows",type=int,default=5000)
    ap.add_argument("--mad",type=float,default=3.0)
    args=ap.parse_args()

    import h5py, numpy as np, pandas as pd
    from scipy.sparse import csr_matrix
    root=Path(args.project_root).resolve(); src=resolve(root,args.discovery)
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)

    with h5py.File(src,"r") as f:
        obs=f["obs"]; raw=f["raw"]; x=raw["X"]; var=raw["var"]
        genes,gene_field=read_genes(var); up=np.char.upper(genes.astype(str))
        masks={
            "mt":np.char.startswith(up,"MT-"),
            "ribo":np.char.startswith(up,"RPS")|np.char.startswith(up,"RPL"),
            "hb":np.isin(up,["HBA1","HBA2","HBB","HBD","HBG1","HBG2"]),
            "platelet":np.isin(up,["PPBP","PF4","NRGN","GNG11","CAVIN2","RGS18"]),
            "ig":np.char.startswith(up,"IGH")|np.char.startswith(up,"IGK")|np.char.startswith(up,"IGL"),
            "b":np.isin(up,["MS4A1","CD79A","CD79B","CD37","CD74","HLA-DRA","CD19","CD22","BANK1","CD83"])
        }
        sample=read_vec(obs,"sample_uuid"); donor=read_vec(obs,"donor_id"); library=read_vec(obs,"library_uuid")
        cohort=read_vec(obs,"Processing_Cohort"); disease=read_vec(obs,"disease")
        n=len(sample); p=len(genes); indptr_all=x["indptr"][:]
        arrays={k:np.zeros(n,float) for k in ["n_counts","mt","ribo","hb","platelet","ig","bcounts"]}
        n_genes=np.zeros(n,np.int32); bdet=np.zeros(n,np.int16)
        for st in range(0,n,args.chunk_rows):
            en=min(n,st+args.chunk_rows); a,b=int(indptr_all[st]),int(indptr_all[en])
            mat=csr_matrix((x["data"][a:b],x["indices"][a:b],indptr_all[st:en+1]-a),shape=(en-st,p))
            arrays["n_counts"][st:en]=np.asarray(mat.sum(1)).ravel(); n_genes[st:en]=np.diff(mat.indptr)
            for name,mask in masks.items():
                if not mask.any(): continue
                sub=mat[:,mask]; vals=np.asarray(sub.sum(1)).ravel()
                if name=="b":
                    arrays["bcounts"][st:en]=vals; bdet[st:en]=np.asarray((sub>0).sum(1)).ravel()
                else: arrays[name][st:en]=vals
            print(f"[QC] {en:,}/{n:,}")

    den=np.maximum(arrays["n_counts"],1)
    cells=pd.DataFrame({"cell_index":np.arange(n),"sample_uuid":sample,"donor_id":donor,"library_uuid":library,"Processing_Cohort":cohort,"disease":disease,"n_counts":arrays["n_counts"],"n_genes":n_genes,"pct_mito":100*arrays["mt"]/den,"pct_ribo":100*arrays["ribo"]/den,"pct_hb":100*arrays["hb"]/den,"pct_platelet":100*arrays["platelet"]/den,"pct_ig":100*arrays["ig"]/den,"blineage_marker_counts":arrays["bcounts"],"n_blineage_markers_detected":bdet})
    metrics=["n_counts","n_genes","pct_mito","pct_ribo","pct_hb","pct_platelet","pct_ig","blineage_marker_counts","n_blineage_markers_detected"]
    cells.to_csv(out/"10_per_cell_raw_qc.csv.gz",index=False,compression="gzip")
    summary(cells,"sample_uuid",metrics).to_csv(out/"11_sample_qc_summary.csv",index=False,encoding="utf-8-sig")
    summary(cells,"library_uuid",metrics).to_csv(out/"12_library_qc_summary.csv",index=False,encoding="utf-8-sig")
    thresholds(cells,"sample_uuid",args.mad).to_csv(out/"13_sample_qc_candidate_thresholds.csv",index=False,encoding="utf-8-sig")
    thresholds(cells,"library_uuid",args.mad).to_csv(out/"14_library_qc_candidate_thresholds.csv",index=False,encoding="utf-8-sig")

    report=f"""# Gate C1-02 raw-count QC v2

- Time: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}
- Source: `{src}`
- Cells: {len(cells):,}
- Samples: {cells.sample_uuid.nunique():,}
- Libraries: {cells.library_uuid.nunique():,}
- Donors: {cells.donor_id.nunique():,}
- Genes: {len(genes):,}
- Gene field used: `{gene_field}`
- Mito genes: {int(masks['mt'].sum())}
- Ribosomal genes: {int(masks['ribo'].sum())}
- Hemoglobin genes: {int(masks['hb'].sum())}
- Platelet markers: {int(masks['platelet'].sum())}
- Immunoglobulin genes: {int(masks['ig'].sum())}
- B-lineage markers: {int(masks['b'].sum())}
- MAD multiplier: {args.mad}

No cell was filtered and source H5AD was not modified.
"""
    (out/"02_RAW_COUNT_QC_SUMMARY.md").write_text(report,encoding="utf-8")
    print(report)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
