"""Independent nonlinear measured-target oracle, candidate v0.1.

Does NOT import or call g2_generator, g2_estimation, a fitted-response output, or a
bootstrap. It shares only immutable calibration parameters and the registry.
Philox random streams are disjoint from the PCG64 simulation/pilot streams.
Population coefficients are conditional arm mean differences, because complete
joint templates are sampled independently of synthetic design rows.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time
import numpy as np

TARGET_NAMES=['beta_B','beta_S_profile','delta_profile','beta_S_cellref','delta_cellref']+[f'beta_bin_{k}' for k in range(1,6)]
TRUTH_SEED=2026101003
EFFORT_LADDER=(64,128,256,512,1024)
BATCHES=16


def independent_scores(count13: np.ndarray, cells: np.ndarray, parameters: dict) -> np.ndarray:
    """An independently written count-to-T0 map; no estimator helper is called.

Caller passes supported draws only. Keep all thirteen categories in denominators.
"""
    C=np.asarray(count13,dtype=float); n=np.asarray(cells,dtype=float)
    if C.ndim!=3 or C.shape[1:]!=(5,13) or n.shape!=C.shape[:2]:
        raise ValueError('Oracle dimensions')
    L=np.add.reduce(C,axis=2)
    if (n<=0).any() or (L<=0).any() or (C<0).any():
        raise ValueError('Oracle invalid counts/denominators')
    pi=np.asarray(parameters['pi']); mu=np.asarray(parameters['mu']); sd=np.asarray(parameters['sd'])
    rates=1.e6*np.divide(C[:,:,:12],L[:,:,None])
    b=1.e6*np.add.reduce(C[:,:,:12],axis=1)/np.add.reduce(L,axis=1)[:,None]
    fixed=np.zeros_like(b); bridge_num=np.zeros_like(b); bridge_den=np.zeros(len(n))
    for k in range(5):
        fixed+=pi[k]*rates[:,k,:]
        mass=pi[k]*L[:,k]/n[:,k]
        bridge_num+=mass[:,None]*rates[:,k,:]; bridge_den+=mass
    mixed=bridge_num/bridge_den[:,None]
    def transform(a):
        return np.add.reduce((np.log(a+0.5)/np.log(2.)-mu)/sd,axis=-1)/12.
    Bs,Ps,Cs=transform(b),transform(fixed),transform(mixed)
    out=np.empty((len(n),10));out[:,0]=Bs;out[:,1]=Ps;out[:,2]=Ps-Bs
    out[:,3]=Cs;out[:,4]=Cs-Bs
    for k in range(5):out[:,5+k]=transform(rates[:,k,:])
    return out


def one_batch(parameters: dict, scenario: dict, index: int, effort: int, batch: int) -> dict:
    """Equal effort for every empirical template; independently simulate both arms.

Poisson rates are first summed over cell-flow origins, then sampled in each
observed bin. A common-minimum Poisson coupling has the correct two marginals.
"""
    rng=np.random.Generator(np.random.Philox(np.random.SeedSequence([TRUTH_SEED,31,index,effort,batch])))
    ntable=np.array(parameters['template_n'],dtype=np.int64)
    htable=np.array(parameters['template_rate'],dtype=float)
    ptable=np.array(parameters['template_probs'],dtype=float)
    tids=np.tile(np.arange(len(ntable)),effort)
    nt=ntable[tids]; h=htable[tids]; probabilities=ptable[tids]
    axis=np.array([-1.,-.5,0.,.5,1.])
    comp=float(scenario['composition_log_tilt']); within=float(scenario['within_bin_log2fc'])
    rare=float(scenario['rare_bin_weight_multiplier']); depth=float(scenario['managed_depth_multiplier'])
    cap=float(scenario['managed_capture_log_tilt']); mis=float(scenario['adjacent_mislabel_probability'])
    basefree=nt-29
    weights0=basefree/basefree.sum(1)[:,None]
    weights1=basefree*np.exp(comp*axis);weights1/=weights1.sum(1)[:,None]
    size=nt.sum(1)-150
    n0=rng.multinomial(size,weights0)+30
    n1=n0.copy() if comp==0 else rng.multinomial(size,weights1)+30
    if rare!=1:
        retained0=rng.binomial(n0[:,0],rare)
        retained1=retained0.copy() if comp==0 else rng.binomial(n1[:,0],rare)
        n0[:,4]+=n0[:,0]-retained0;n0[:,0]=retained0
        n1[:,4]+=n1[:,0]-retained1;n1[:,0]=retained1
    def flow_counts(n):
        f=np.zeros((len(n),5,5),dtype=np.int64)
        for origin in range(5):
            if mis==0:
                f[:,origin,origin]=n[:,origin]
            else:
                probs=np.zeros(5);probs[origin]=1.-mis
                available=list(range(max(0,origin-1),min(5,origin+2)))
                available.remove(origin)
                for dest in available:probs[dest]=mis/len(available)
                f[:,origin,:]=rng.multinomial(n[:,origin],probs)
        return f
    f0=flow_counts(n0);f1=f0.copy() if comp==0 else flow_counts(n1)
    obs0=np.add.reduce(f0,axis=1);obs1=np.add.reduce(f1,axis=1)
    rate0=h[:,:,None]*probabilities
    rate1=h[:,:,None]*depth*np.exp(cap*axis)[None,:,None]*probabilities
    rate1[:,:,:12]*=2.**within
    lam0=np.einsum('isd,isg->idg',f0,rate0,optimize=True)
    lam1=np.einsum('isd,isg->idg',f1,rate1,optimize=True)
    shared_rate=np.minimum(lam0,lam1)
    shared=rng.poisson(shared_rate)
    Y0=shared+rng.poisson(np.maximum(lam0-shared_rate,0.))
    Y1=shared+rng.poisson(np.maximum(lam1-shared_rate,0.))
    stats=[]
    for Y,n in ((Y0,obs0),(Y1,obs1)):
        valid=(n>=30).all(1)&(Y.sum(2)>0).all(1)
        s=independent_scores(Y[valid],n[valid],parameters)
        stats.append({'accepted':int(valid.sum()),'sum':s.sum(0),'sum_sq':(s*s).sum(0)})
    return {'attempted_per_arm':len(tids),'arms':stats}


def summarize(batches: list[dict], parameters: dict, exact_null: bool) -> list[dict]:
    ns=np.array([[b['arms'][a]['accepted'] for a in (0,1)] for b in batches],dtype=float)
    sums=np.array([[b['arms'][a]['sum'] for a in (0,1)] for b in batches])
    sq=np.array([[b['arms'][a]['sum_sq'] for a in (0,1)] for b in batches])
    if (ns.sum(0)<=0).any():raise ValueError('No accepted oracle donors for an arm')
    mean=sums.sum(0)/ns.sum(0)[:,None]
    var=np.maximum(sq.sum(0)/ns.sum(0)[:,None]-mean**2,0.)
    # Delta-method MCSE for ratios of means with independently replicated batches.
    influence=(sums[:,1,:]-ns[:,1,None]*mean[1])/ns[:,1].mean()
    influence-=(sums[:,0,:]-ns[:,0,None]*mean[0])/ns[:,0].mean()
    mcse=np.std(influence,axis=0,ddof=1)/np.sqrt(len(batches))
    X=np.array(parameters['synthetic_design'],dtype=float)
    # Leverage is a property of the immutable design, not an estimated outcome.
    W=np.linalg.solve(X.T@X,X.T)[1]
    se=np.sqrt(np.sum(W[X[:,1]==0]**2)*var[0]+np.sum(W[X[:,1]==1]**2)*var[1])
    if (se<=0).any():raise ValueError('Degenerate target variability')
    prob=ns.sum(0)/sum(b['attempted_per_arm'] for b in batches)
    joint=float(prob[0]**31*prob[1]**37)
    rows=[]
    for j,name in enumerate(TARGET_NAMES):
        truth=0. if exact_null else float(mean[1,j]-mean[0,j])
        mse=0. if exact_null else float(mcse[j])
        rows.append({'target_id':name,'truth':truth,'truth_mcse':mse,
         'truth_mc_95_halfwidth':1.96*mse,'typical_coefficient_se':float(se[j]),
         'mcse_over_typical_se':mse/se[j],'precision_pass':bool(mse<=.01*se[j]),
         'true_null_registered':exact_null,'truth_basis':'EXACT_ARM_SYMMETRY' if exact_null else 'INDEPENDENT_CONDITIONAL_MONTE_CARLO',
         'accepted_donors_arm0':int(ns[:,0].sum()),'accepted_donors_arm1':int(ns[:,1].sum()),
         'attempted_donors_per_arm':int(sum(b['attempted_per_arm'] for b in batches)),
         'support_probability_arm0':float(prob[0]),'support_probability_arm1':float(prob[1]),
         'whole68_support_probability':joint,
         'target_domain':'observed-bin count measurement conditional on support; not latent-state oracle'})
    return rows


def source_hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_scenario(model_path: Path, registry_path: Path, index: int, output: Path,
                 effort_cap: int=1024) -> dict:
    if effort_cap not in EFFORT_LADDER:raise ValueError('Cap must be on the fixed ladder')
    parameters=json.loads(model_path.read_text())
    with registry_path.open(encoding='utf-8-sig') as handle:
        rows=list(csv.DictReader(handle))
    sc=rows[index]
    if output.exists():raise FileExistsError(output)
    output.mkdir(parents=True)
    exact=sc['scenario_id'] in ('C0_R0','C0_R1','C0_R3')
    history=[];t=time.perf_counter();result_rows=None
    for effort in EFFORT_LADDER:
        batches=[one_batch(parameters,sc,index,effort,b) for b in range(BATCHES)]
        result_rows=summarize(batches,parameters,exact)
        for r in result_rows:r.update(scenario_id=sc['scenario_id'],effort_per_template_per_batch=effort,batches=BATCHES)
        history.append({'effort_per_template_per_batch':effort,
                        'all_precision_pass':all(r['precision_pass'] for r in result_rows),
                        'max_mcse_over_typical_se':max(r['mcse_over_typical_se'] for r in result_rows)})
        # Store the aggregate per-batch sufficient summaries, not an estimator's output.
        serial=[]
        for b in batches:
            serial.append({'attempted_per_arm':b['attempted_per_arm'],
              'arms':[{k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in arm.items()} for arm in b['arms']]})
        (output/f'batches_effort_{effort}.json').write_text(json.dumps(serial,separators=(',',':'))+'\n')
        if history[-1]['all_precision_pass'] or effort==effort_cap:break
    with (output/'truth.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=result_rows[0].keys());writer.writeheader();writer.writerows(result_rows)
    passed=all(r['precision_pass'] for r in result_rows)
    receipt={'status':'PASS_TRUTH_PRECISION_CANDIDATE' if passed else 'HOLD_TRUTH_PRECISION',
       'scenario_id':sc['scenario_id'],'history':history,'effort_cap':effort_cap,
       'independent_truth_code_sha256':source_hash(__file__),'model_sha256':source_hash(model_path),
       'scenario_registry_sha256':source_hash(registry_path),'truth_csv_sha256':source_hash(output/'truth.csv'),
       'elapsed_seconds':time.perf_counter()-t,'real_effects_fitted':False,'G2_PASS':False,
       'scope':'candidate observed measurement law only; does not validate latent identities'}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True)
    p.add_argument('--registry',type=Path,required=True);p.add_argument('--scenario-index',type=int,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--effort-cap',type=int,default=1024)
    a=p.parse_args();print(json.dumps(run_scenario(a.model,a.registry,a.scenario_index,a.output,a.effort_cap),indent=2))
