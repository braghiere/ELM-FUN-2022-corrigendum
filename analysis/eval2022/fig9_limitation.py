#!/usr/bin/env python3
"""Braghiere et al. (2022) Figure 9 redrawn: N vs P vs co-limitation from the stoichiometric-homeostasis ratio
R = (leaf N : leaf P) / (retranslocated N : retranslocated P), using LEAFN, LEAFP (pools) and NRETRANS, PRETRANS (fluxes).
The paper gives no thresholds; they are CALIBRATED once on the published product (1994-2005) so that 6.1 % of natural land
is N-limited (low R) and 13.9 % P-limited (high R), then applied unchanged to every run. Natural land = cells with
vegetated landunit, excluding crop PFTs (>50 % of PCT_NAT_PFT in 15,16), urban and glacier as in Du et al. (2020).
Usage: fig9_limitation.py <period> <calibration_label> <label1> [<label2> ...]"""
import sys, json, numpy as np, netCDF4 as nc, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; from matplotlib.colors import ListedColormap
period,cal=sys.argv[1],sys.argv[2]; labels=sys.argv[3:]; D='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/'
def R_and_mask(lab):
    d=nc.Dataset(D+f'{lab}_{period}_h0mean.nc'); f=lambda v: np.where(np.abs(np.ma.filled(d[v][:].astype(float),np.nan))<1e30,np.ma.filled(d[v][:].astype(float),np.nan),np.nan)
    ln,lp,rn,rp=f('LEAFN'),f('LEAFP'),f('NRETRANS'),f('PRETRANS'); R=(ln/lp)/(rn/rp)
    A=np.nan_to_num(d['area'][:]*1e6*d['landfrac'][:]); pct=f('PCT_NAT_PFT') if 'PCT_NAT_PFT' in d.variables else None
    nat=np.isfinite(R)&(A>0)&(lp>1e-6)&(rp>1e-15)
    if pct is not None: nat&=(np.nansum(pct[15:17],axis=0)<50)
    return R,A,nat,d['lat'][:],d['lon'][:]
Rc,Ac,natc,_,_=R_and_mask(cal); logR=np.log(Rc[natc]); w=Ac[natc]; o=np.argsort(logR); cw=np.cumsum(w[o])/w.sum()
lo=float(np.exp(logR[o][np.searchsorted(cw,0.061)])); hi=float(np.exp(logR[o][np.searchsorted(cw,1-0.139)]))
print(f'   thresholds calibrated on {cal} {period}: N-limited if R < {lo:.3f}, P-limited if R > {hi:.3f} (co-limited between); log-symmetry check: ln(lo)={np.log(lo):+.2f}, ln(hi)={np.log(hi):+.2f}')
json.dump({'calibration':cal,'period':period,'R_lo':lo,'R_hi':hi},open(f'fig9_thresholds_{period}.json','w'),indent=1)
n=len(labels); fig,ax=plt.subplots(1,n,figsize=(6.2*n,3.4),squeeze=False); cmap=ListedColormap(['#e34948','#bfbfbf','#2a78d6']); res={}
for j,l in enumerate(labels):
    R,A,nat,lat,lon=R_and_mask(l); cls=np.where(R<lo,0,np.where(R>hi,2,1)).astype(float); cls[~nat]=np.nan
    fr=[100*A[nat&(cls==k)].sum()/A[nat].sum() for k in (0,1,2)]; res[l]={'N_limited_%':fr[0],'co_limited_%':fr[1],'P_limited_%':fr[2]}
    LON,LAT=np.meshgrid(lon,lat); ax[0,j].pcolormesh(LON,LAT,cls,cmap=cmap,vmin=-0.5,vmax=2.5,shading='auto'); ax[0,j].set_title(f'{l}: N-limited {fr[0]:.1f} %  co-limited {fr[1]:.1f} %  P-limited {fr[2]:.1f} %',fontsize=9)
    ax[0,j].set_xticks([]); ax[0,j].set_yticks([]); [ax[0,j].spines[s].set_visible(False) for s in ax[0,j].spines]
fig.suptitle(f'Braghiere et al. (2022) Figure 9 redrawn — {period}; paper: N 6.1 %, co 80.0 %, P 13.9 % (red = N, gray = co, blue = P); thresholds R<{lo:.2f} / R>{hi:.2f} calibrated on {cal}',fontsize=9)
out=f'/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/fig9_{period}_'+'_'.join(labels)+'.png'; plt.savefig(out,dpi=120,bbox_inches='tight'); print('   wrote',out); print('  ',json.dumps(res))
