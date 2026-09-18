#!/usr/bin/env python3
"""Braghiere et al. (2022) Figures 5, 6, 7 and S5 re-drawn side by side. Columns = runs (e.g. published_FUNP control corrected),
plus a last column with the difference (last − second-to-last) when >=2 runs. Rows = pathway fields.
Usage: fig_maps.py <period> <fig: 5|6|7|S5> <label1> [<label2> ...]
Fig 5: N pathways (g N m-2 yr-1): symbiotic fixation, direct root, retranslocation, AM, EcM.
Fig 6: P pathways (g P m-2 yr-1): direct root, retranslocation, AM, EcM.
Fig 7: retranslocation efficiency (%) of N and P = retranslocated / nutrient in dying leaves before senescence,
       with leaf-litter nutrient estimated as LEAFC_TO_LITTER * (LEAFN/LEAFC) [paper gives no variable list; documented choice].
Fig S5: C use ratio (%) = C spent on N (P) acquisition / available C (AVAILC = GPP − maintenance respiration)."""
import sys, numpy as np, netCDF4 as nc, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
period,fig=sys.argv[1],sys.argv[2]; labels=sys.argv[3:]; D='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/'; spy=86400*365.
def fld(d,v): x=np.ma.filled(d[v][:].astype(float),np.nan); return np.where(np.abs(x)<1e30,x,np.nan)
def rows(d):
    if fig=='5': return [('Symbiotic N fixation',fld(d,'NFIX')*spy,'g N m$^{-2}$ yr$^{-1}$'),('Direct root N uptake',fld(d,'NNONMYC')*spy,'g N m$^{-2}$ yr$^{-1}$'),('N retranslocation',fld(d,'NRETRANS')*spy,'g N m$^{-2}$ yr$^{-1}$'),('AM N uptake',fld(d,'NAM')*spy,'g N m$^{-2}$ yr$^{-1}$'),('EcM N uptake',fld(d,'NECM')*spy,'g N m$^{-2}$ yr$^{-1}$')]
    if fig=='6': return [('Direct root P uptake',fld(d,'PNONMYC')*spy,'g P m$^{-2}$ yr$^{-1}$'),('P retranslocation',fld(d,'PRETRANS')*spy,'g P m$^{-2}$ yr$^{-1}$'),('AM P uptake',fld(d,'PAM')*spy,'g P m$^{-2}$ yr$^{-1}$'),('EcM P uptake',fld(d,'PECM')*spy,'g P m$^{-2}$ yr$^{-1}$')]
    if fig=='7':
        lc=fld(d,'LEAFC_TO_LITTER'); ln=fld(d,'LEAFN')/np.where(fld(d,'LEAFC')>0,fld(d,'LEAFC'),np.nan); lp=fld(d,'LEAFP')/np.where(fld(d,'LEAFC')>0,fld(d,'LEAFC'),np.nan)
        rn=fld(d,'NRETRANS'); rp=fld(d,'PRETRANS'); litn=lc*ln; litp=lc*lp
        return [('N retranslocation efficiency',100*rn/np.where(litn>0,litn,np.nan),'%'),('P retranslocation efficiency',100*rp/np.where(litp>0,litp,np.nan),'%')]
    if fig=='S5':
        a=np.where(fld(d,'AVAILC')>0,fld(d,'AVAILC'),np.nan); return [('C use ratio, N uptake',100*fld(d,'NPP_NUPTAKE')/a,'%'),('C use ratio, P uptake',100*fld(d,'NPP_PUPTAKE')/a,'%')]
data={l:nc.Dataset(D+f'{l}_{period}_h0mean.nc') for l in labels}; lat=data[labels[0]]['lat'][:]; lon=data[labels[0]]['lon'][:]
R={l:rows(data[l]) for l in labels}; nr=len(R[labels[0]]); diff=len(labels)>=2; nc_=len(labels)+(1 if diff else 0)
lf=np.nan_to_num(fld(data[labels[0]],'landfrac')); land=lf>0.05
fig_,ax=plt.subplots(nr,nc_,figsize=(4.6*nc_,2.35*nr+0.8),squeeze=False); LON,LAT=np.meshgrid(lon,lat)
for i in range(nr):
    name,_,unit=R[labels[0]][i]; allv=np.concatenate([R[l][i][1][land] for l in labels]); vmax=np.nanpercentile(allv,98); vmax=vmax if vmax>0 else 1
    for j,l in enumerate(labels):
        x=np.where(land,R[l][i][1],np.nan); m=ax[i,j].pcolormesh(LON,LAT,x,cmap='YlGnBu',vmin=0,vmax=vmax,shading='auto'); ax[i,j].set_title(f'{name}\n{l}',fontsize=8.5)
        gm=np.nansum(np.nan_to_num(x)*np.nan_to_num(data[l]['area'][:])*lf)/np.nansum(np.nan_to_num(data[l]['area'][:])*lf*np.isfinite(x))
        ax[i,j].text(0.01,0.02,f'land mean {gm:.2f} {unit.replace("$","")}',transform=ax[i,j].transAxes,fontsize=6.5,color='#333')
    plt.colorbar(m,ax=ax[i,:len(labels)].tolist(),shrink=0.85,pad=0.01,label=unit)
    if diff:
        a,b=labels[-2],labels[-1]; dx=np.where(land,R[b][i][1]-R[a][i][1],np.nan); lim=np.nanpercentile(np.abs(dx[land]),98); lim=lim if lim>0 else 1e-9
        m2=ax[i,-1].pcolormesh(LON,LAT,dx,cmap='RdBu_r',vmin=-lim,vmax=lim,shading='auto'); ax[i,-1].set_title(f'{name}\n{b} − {a}',fontsize=8.5); plt.colorbar(m2,ax=ax[i,-1],shrink=0.85,pad=0.01,label=unit)
for a_ in ax.ravel(): a_.set_xticks([]); a_.set_yticks([]); [a_.spines[s].set_visible(False) for s in a_.spines]
fig_.suptitle(f'Braghiere et al. (2022) Figure {fig} redrawn — {period} means',fontsize=11,y=0.995)
out=f'/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/fig{fig}_{period}_'+'_'.join(labels)+'.png'; plt.savefig(out,dpi=120,bbox_inches='tight'); print('   wrote',out)
