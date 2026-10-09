"""Candidate donor x bin sufficient-count generator. SIMULATION ONLY.

No fitted disease effects enter this generator. The background category is part
of every generated library. Whole templates carry joint empirical heterogeneity.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

OUTER_SEED = 2026101002
PILOT_STAGE = 11
FULL_STAGE = 21


def load_model(path: str | Path) -> dict:
    model = json.loads(Path(path).read_text(encoding='utf-8'))
    if model.get('data_kind') != 'CALIBRATION_NO_REAL_EFFECT':
        raise ValueError('Only an explicitly outcome-free calibration object is accepted')
    for field in ('template_n','template_rate','template_probs','mu','sd','pi','synthetic_design','tilt_axis'):
        model[field] = np.asarray(model[field],dtype=np.int64 if field=='template_n' else float)
        if not np.isfinite(model[field]).all():
            raise ValueError('Nonfinite calibration field: '+field)
    n,h,p=model['template_n'],model['template_rate'],model['template_probs']
    if n.shape!=(68,5) or h.shape!=n.shape or p.shape!=(68,5,13):
        raise ValueError('Unexpected joint-template dimensions')
    if (n<30).any() or (h<=0).any() or (p<=0).any() or not np.allclose(p.sum(-1),1,atol=1e-12,rtol=0):
        raise ValueError('Invalid count/rate/full-background probability calibration')
    if model['mu'].shape!=(12,) or model['sd'].shape!=(12,) or (model['sd']<=0).any():
        raise ValueError('Invalid T0')
    if model['pi'].shape!=(5,) or (model['pi']<=0).any() or not np.isclose(model['pi'].sum(),1,atol=1e-12):
        raise ValueError('Invalid pi_ref')
    x=model['synthetic_design']
    if x.shape!=(68,4) or not np.all(x[:,0]==1) or np.sum(x[:,1]==0)!=31 or np.sum(x[:,1]==1)!=37:
        raise ValueError('The pilot inherits the fixed 68-row, 31/37 design')
    if model.get('true_template_labels_present') is not False:
        raise ValueError('Template disease labels must be absent')
    return model


def scenarios(path: str | Path) -> list[dict]:
    with Path(path).open(encoding='utf-8-sig',newline='') as handle:
        rows=list(csv.DictReader(handle))
    for r in rows:
        for field in ('composition_log_tilt','within_bin_log2fc','rare_bin_weight_multiplier',
                      'managed_depth_multiplier','adjacent_mislabel_probability','managed_capture_log_tilt'):
            r[field]=float(r[field])
        for field in ('outer_attempts','inner_paired_bootstraps'):
            r[field]=int(r[field])
    if len(rows)!=25 or [r['scenario_id'] for r in rows]!=[f'C{c}_R{r}' for c in range(5) for r in range(5)]:
        raise ValueError('The original 25-scenario order is required')
    if any(r['outer_attempts']!=2000 or r['inner_paired_bootstraps']!=2000 for r in rows):
        raise ValueError('Registered replicate counts have changed')
    return rows


def stream(scenario_index: int, attempt: int, component: int, stage: int=PILOT_STAGE) -> np.random.Generator:
    if not(0<=scenario_index<25 and attempt>=1 and component>=0):
        raise ValueError('Invalid counter-addressed stream key')
    return np.random.default_rng(np.random.SeedSequence([OUTER_SEED,stage,scenario_index,attempt,component]))


def transition(probability: float) -> np.ndarray:
    if not 0<=probability<=1:
        raise ValueError('Invalid adjacent-mislabel probability')
    m=np.eye(5)*(1-probability)
    for k in range(5):
        neighbors=[j for j in (k-1,k+1) if 0<=j<5]
        for j in neighbors:
            m[k,j]=probability/len(neighbors)
    return m


def generate(model: dict, scenario: dict, scenario_index: int, attempt: int, stage: int=PILOT_STAGE) -> dict:
    """One attempt; never redraw to obtain support. All arms are synthetic."""
    x=model['synthetic_design'].copy(); d=x[:,1]
    ids=stream(scenario_index,attempt,0,stage).integers(0,68,size=68)
    nt=model['template_n'][ids]; h=model['template_rate'][ids]; prob=model['template_probs'][ids]
    weights=(nt-30+1)*np.exp(d[:,None]*scenario['composition_log_tilt']*model['tilt_axis'][None,:])
    weights/=weights.sum(1,keepdims=True)
    n=30+stream(scenario_index,attempt,1,stage).multinomial(nt.sum(1)-150,weights)
    rare=scenario['rare_bin_weight_multiplier']
    if rare!=1:
        retained=stream(scenario_index,attempt,2,stage).binomial(n[:,0],rare)
        n[:,4]+=n[:,0]-retained; n[:,0]=retained
    capture=h*np.power(scenario['managed_depth_multiplier'],d[:,None])
    capture*=np.exp(d[:,None]*scenario['managed_capture_log_tilt']*model['tilt_axis'][None,:])
    rates=capture[:,:,None]*prob
    rates[:,:,:12]*=np.exp2(d[:,None,None]*scenario['within_bin_log2fc'])
    q=scenario['adjacent_mislabel_probability']
    rng=stream(scenario_index,attempt,3,stage)
    flow=np.zeros((68,5,5),dtype=np.int64)
    M=transition(q)
    for k in range(5):
        if q==0:
            flow[:,k,k]=n[:,k]
        else:
            flow[:,k,:]=rng.multinomial(n[:,k],M[k])
    obs_n=flow.sum(1)
    # Different from the truth engine: independently draw each origin/destination
    # category, then aggregate counts. Never normalize on the twelve-gene subset.
    y=np.zeros((68,5,13),dtype=np.int64)
    prng=stream(scenario_index,attempt,4,stage)
    for origin in range(5):
        for dest in range(5):
            if M[origin,dest]>0:
                y[:,dest,:]+=prng.poisson(flow[:,origin,dest,None]*rates[:,origin,:])
    L=y.sum(2)
    ok=bool((obs_n>=30).all() and (L>0).all())
    return {'data_kind':'SIMULATED_ONLY','n':obs_n,'categories':y,'X':x,
            'template_indices':ids,'flow':flow,'latent_n':n,
            'scenario_id':scenario['scenario_id'],'attempt':attempt,
            'support_status':'SUPPORTED' if ok else 'SUPPORT_STOP',
            'min_observed_cells':int(obs_n.min()),'zero_library_bins':int((L==0).sum()),
            'under_supported_bins':int((obs_n<30).sum())}


def data_digest(data: dict) -> str:
    h=hashlib.sha256()
    for key in ('n','categories','X','template_indices','flow'):
        a=np.ascontiguousarray(data[key]); h.update(key.encode()); h.update(a.dtype.str.encode())
        h.update(str(a.shape).encode()); h.update(a.tobytes())
    return h.hexdigest()
