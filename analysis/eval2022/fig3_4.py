#!/usr/bin/env python3
"""Braghiere et al. (2022) Figures 3a (zonal NPP 1994-2005), 4a (global NPP 1850-2010 with box plots), S10 (GPP, AR, HR), S11a (cumulative NBP)
from data/<label>_series.npz. Usage: fig3_4.py <label1> [<label2> ...]  (published_ELM published_FUN2 published_FUNP control corrected ...)
Benchmarks (MODIS NPP, IGBP NPP, CMIP6) are drawn if data/benchmarks/{modis_npp_zonal.npz, igbp_npp_zonal.npz, cmip6_npp_zonal.npz} exist."""
import sys, os, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
INVALID_FROM=2009   # archived products: CO2 forcing file ends 2007 -> PCO2 collapses from mid-2009; mask published series from 2009
labels=sys.argv[1:]; D='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/'; S={}
for l in labels:
    z=dict(np.load(D+f'{l}_series.npz'))
    if l.startswith('published'):
        bad=z['years']>=INVALID_FROM
        for v in ('GPP','NPP','AR','HR','NBP'):
            if v in z: z[v]=np.where(bad,np.nan,z[v])
    S[l]=z
COL={'published_ELM':'#7f7f7f','published_FUN2':'#eda100','published_FUNP':'#2a78d6','control':'#1baf7a','corrected':'#eb6834'}
def c(l): return COL.get(l,'#4a3aa7')
fig,ax=plt.subplots(2,2,figsize=(15,9))
# 3a zonal NPP
for l in labels:
    z=S[l]['zonal_npp_1994_2005']; ax[0,0].plot(S[l]['lat'],z,color=c(l),lw=2,label=l)
for bm,nm,st in (('modis_npp_zonal.npz','MODIS NPP','k--'),('igbp_npp_zonal.npz','IGBP NPP','k:'),('cmip6_npp_zonal.npz','CMIP6 (11 models)','k-.')):
    p=D+'benchmarks/'+bm
    if os.path.exists(p): b=np.load(p); ax[0,0].plot(b['lat'],b['npp'],st,lw=1.5,label=nm)
ax[0,0].set_xlabel('latitude'); ax[0,0].set_ylabel('zonal mean NPP 1994–2005 (g C m$^{-2}$ yr$^{-1}$)'); ax[0,0].legend(fontsize=8,frameon=False); ax[0,0].grid(alpha=.3); ax[0,0].set_title('Fig. 3a',loc='left')
# 4a global NPP series + box
for l in labels:
    y=S[l]['years']; v=S[l]['NPP']; m=y>=1855; ax[0,1].plot(y[m],v[m],color=c(l),lw=1.6,label=f'{l} (mean {np.nanmean(v[m]):.1f})')
ax[0,1].set_ylabel('global NPP (Pg C yr$^{-1}$)'); ax[0,1].set_title(f'Fig. 4a  (archived products masked from {INVALID_FROM}: CO$_2$ forcing file ends 2007)',loc='left',fontsize=10); ax[0,1].legend(fontsize=8,frameon=False); ax[0,1].grid(alpha=.3)
ins=ax[0,1].inset_axes([0.78,0.08,0.2,0.5]); ins.boxplot([S[l]['NPP'][(S[l]['years']>=1855)&np.isfinite(S[l]['NPP'])] for l in labels],widths=0.6,medianprops=dict(color='k')); ins.set_xticks([]); ins.tick_params(labelsize=7); ins.set_title('1855–2010',fontsize=7)
# S10: GPP, AR, HR
for l in labels:
    y=S[l]['years']
    for v,ls in (('GPP','-'),('AR','--'),('HR',':')): ax[1,0].plot(y,S[l][v],ls,color=c(l),lw=1.4,label=f'{l} {v}')
ax[1,0].set_ylabel('Pg C yr$^{-1}$'); ax[1,0].set_title('Fig. S10: GPP (solid), AR (dashed), HR (dotted)',loc='left'); ax[1,0].legend(fontsize=6.5,frameon=False,ncol=2); ax[1,0].grid(alpha=.3)
# S11a cumulative NBP
for l in labels:
    if 'NBP' in S[l] and np.isfinite(S[l]['NBP']).any(): ax[1,1].plot(S[l]['years'],np.nancumsum(S[l]['NBP']),color=c(l),lw=1.6,label=l)
ax[1,1].set_ylabel('cumulative NBP since 1850 (Pg C)'); ax[1,1].set_title('Fig. S11a',loc='left'); ax[1,1].legend(fontsize=8,frameon=False); ax[1,1].grid(alpha=.3)
plt.tight_layout(); out='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/fig3_4_S10_S11_'+'_'.join(labels)+'.png'; plt.savefig(out,dpi=120); print('   wrote',out)
for l in labels: y=S[l]['years']; m=(y>=1994)&(y<=2005); print(f"   {l}: NPP 1994-2005 mean {np.nanmean(S[l]['NPP'][m]):.1f} Pg C/yr; GPP {np.nanmean(S[l]['GPP'][m]):.1f}; CUE {100*np.nanmean(S[l]['NPP'][m])/np.nanmean(S[l]['GPP'][m]):.1f} %")
