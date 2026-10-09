"""Frozen-score operators and actual paired donor bootstrap for simulated data.

The executable workflow accepts SIMULATED_ONLY objects, never real WP2 responses.
Four-column OLS uses checked partial pivoting, avoiding the known Windows LAPACK
failure path; weighted results are tested against independent expanded-row OLS.
"""
from __future__ import annotations
import numpy as np

TARGETS=['beta_B','beta_S_profile','delta_profile','beta_S_cellref','delta_cellref']+[f'beta_bin_{i}' for i in range(1,6)]


def score(cpm: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    if (cpm<0).any() or not np.isfinite(cpm).all() or (sd<=0).any():
        raise ValueError('Invalid CPM or T0 scale')
    return np.mean((np.log2(cpm+0.5)-mu)/sd,axis=-1)


def responses(data: dict, model: dict) -> np.ndarray:
    if data.get('data_kind')!='SIMULATED_ONLY':
        raise PermissionError('This runner does not unlock real WP2 effects')
    n=np.asarray(data['n']); Y=np.asarray(data['categories'])
    if n.shape!=(68,5) or Y.shape!=(68,5,13) or not np.isfinite(Y).all() or (Y<0).any():
        raise ValueError('Invalid sufficient counts')
    L=Y.sum(2)
    if (n<30).any() or (L<=0).any():
        raise ValueError('SUPPORT_STOP')
    m=Y[:,:,:12]*1e6/L[:,:,None]
    pooled=Y[:,:,:12].sum(1)*1e6/L.sum(1)[:,None]
    profile=np.einsum('k,ikg->ig',model['pi'],m)
    weights=(L/n)*model['pi']; weights/=weights.sum(1,keepdims=True)
    cellref=np.einsum('ik,ikg->ig',weights,m)
    b=score(pooled,model['mu'],model['sd'])
    p=score(profile,model['mu'],model['sd'])
    c=score(cellref,model['mu'],model['sd'])
    bins=score(m,model['mu'],model['sd'])
    out=np.column_stack([b,p,p-b,c,c-b,bins])
    if out.shape!=(68,10) or not np.isfinite(out).all():
        raise ValueError('Nonfinite score or target shape')
    return out


def solve_batch(A: np.ndarray, B: np.ndarray, tol: float=1e-12) -> tuple[np.ndarray,np.ndarray]:
    """Batched Gauss-Jordan partial-pivot solve with explicit failure flags."""
    A=np.array(A,dtype=float,copy=True); B=np.array(B,dtype=float,copy=True)
    if A.ndim!=3 or A.shape[1:]!=(4,4) or B.shape[:2]!=A.shape[:2]:
        raise ValueError('Requires batched four-column designs')
    count=len(A); ii=np.arange(count)
    good=np.isfinite(A).all((1,2)) & np.isfinite(B).all((1,2))
    scale=np.maximum(np.max(np.abs(A),axis=(1,2)),1.)
    for j in range(4):
        piv=j+np.argmax(np.abs(A[:,j:,j]),axis=1)
        t=A[:,j,:].copy(); A[:,j,:]=A[ii,piv,:]; A[ii,piv,:]=t
        t=B[:,j,:].copy(); B[:,j,:]=B[ii,piv,:]; B[ii,piv,:]=t
        divisor=A[:,j,j].copy()
        valid=np.abs(divisor)>tol*scale; good &= valid
        divisor=np.where(valid,divisor,1.)
        A[:,j,:]/=divisor[:,None]; B[:,j,:]/=divisor[:,None]
        factors=A[:,:,j].copy(); factors[:,j]=0.
        A-=factors[:,:,None]*A[:,j,None,:]
        B-=factors[:,:,None]*B[:,j,None,:]
    good &= np.isfinite(B).all((1,2))
    B[~good]=np.nan
    return B,good


def weighted_coefs(X: np.ndarray, Y: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
    X=np.asarray(X,dtype=float); Y=np.asarray(Y,dtype=float); w=np.asarray(weights,dtype=float)
    if X.ndim!=2 or X.shape[1]!=4 or Y.ndim!=2 or Y.shape[0]!=X.shape[0] or w.ndim!=2 or w.shape[1]!=len(X):
        raise ValueError('Shape mismatch')
    if not np.isfinite(X).all() or not np.isfinite(Y).all() or not np.isfinite(w).all() or (w<0).any():
        raise ValueError('Nonfinite or negative input')
    # Column scaling is fixed by the original design, not bootstrap-specific;
    # the disease dummy already has scale 1 and retains its coefficient units.
    scale=np.maximum(np.max(np.abs(X),axis=0),1.)
    xs=X/scale
    A=np.empty((len(w),4,4)); B=np.empty((len(w),4,Y.shape[1]))
    for j in range(4):
        for k in range(4): A[:,j,k]=w@(xs[:,j]*xs[:,k])
        B[:,j,:]=w@(xs[:,j,None]*Y)
    coef,ok=solve_batch(A,B)
    return coef[:,1,:]/scale[1],ok


def paired_bootstrap(X: np.ndarray, Y: np.ndarray, rng: np.random.Generator,
                     attempts: int=2000) -> dict:
    if attempts!=2000:
        raise ValueError('The technical pilot uses the actual frozen 2000-attempt interval')
    d=X[:,1]; idx0=np.flatnonzero(d==0); idx1=np.flatnonzero(d==1)
    if len(idx0)!=31 or len(idx1)!=37 or len(d)!=68:
        raise ValueError('Missing arm or changed fixed design')
    inds=np.concatenate([rng.choice(idx0,(attempts,len(idx0)),replace=True),
                         rng.choice(idx1,(attempts,len(idx1)),replace=True)],axis=1)
    w=np.zeros((attempts,len(X)),dtype=float)
    np.add.at(w,(np.repeat(np.arange(attempts),len(X)),inds.ravel()),1.)
    est,success=weighted_coefs(X,Y,w)
    point,pointok=weighted_coefs(X,Y,np.ones((1,len(X))))
    if not pointok[0]: raise ValueError('Rank-deficient point design')
    failures=int((~success).sum())
    ci=np.quantile(est[success],[.025,.975],axis=0).T if success.any() else np.full((Y.shape[1],2),np.nan)
    return {'point':point[0],'estimates':est,'success':success,'interval':ci,
            'attempted':attempts,'failures':failures,'no_replenishment':True,
            'gate':'TECHNICAL_INTERVAL_COMPUTED' if failures<=20 else 'HOLD_NUMERICAL_IMPLEMENTATION',
            'indices':inds}
