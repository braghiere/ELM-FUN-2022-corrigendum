#!/usr/bin/env python3
"""Braghiere et al. (2022) Figure 8 redrawn side by side. Columns = runs.
(a,c) C used by N and P acquisition per biome, g C per m2 of the biome's PFT area per yr, mean ± 1 SD across grid cells:
      from the PFT-level stream (*_pftmean.nc, NPP_NUPTAKE / NPP_PUPTAKE, weights pfts1d_wtgcell * area * landfrac).
(b,d) relative pathway shares (%) from the gridded pathway costs (*_h0mean.nc: NPP_NACTIVE, NPP_NNONMYC, NPP_NRETRANS, NPP_NFIX;
      NPP_PACTIVE, NPP_PNONMYC, NPP_PRETRANS) summed over grid cells whose dominant natural PFT belongs to the biome.
      [The PFT stream carries no pathway costs and the N/COST reconstruction does not close, so shares are cell-based.]
Biome mapping (paper does not list PFTs; SI Fig S4 groups grasslands incl. C3 crop):
  EBF = PFT 4,5 | ENF = 1,2 | DBF = 6,7,8 | grassland = 12,13,14,15 | shrubland = 9,10,11 | DNF = 3.
Usage: fig8_biomes.py <period> <label1> [<label2> ...]"""
import sys, numpy as np, netCDF4 as nc, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
period=sys.argv[1]; labels=sys.argv[2:]; D='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/'; spy=86400*365.
BIOMES=[('Evergreen broadleaf forest',[4,5]),('Evergreen needleleaf forest',[1,2]),('Deciduous broadleaf forest',[6,7,8]),('Grassland',[12,13,14,15]),('Shrubland',[9,10,11]),('Deciduous needleleaf forest',[3])]
COLS=['#2a78d6','#eb6834','#1baf7a','#eda100']
def clean(x): x=np.array(x,dtype=float); return np.where(np.abs(x)<1e30,x,np.nan)
def stats(lab):
    pf=nc.Dataset(D+f'{lab}_{period}_pftmean.nc'); h0=nc.Dataset(D+f'{lab}_{period}_h0mean.nc')
    wt=np.array(pf['pft_wtgcell'][:]); A=np.nan_to_num(h0['area'][:]*1e6*h0['landfrac'][:]); lf=np.nan_to_num(h0['landfrac'][:])
    pct=clean(h0['PCT_NAT_PFT'][:]); dom=np.nanargmax(np.nan_to_num(pct),axis=0)   # dominant natural PFT per cell
    tot={'N':clean(pf['NPP_NUPTAKE'][:]),'P':clean(pf['NPP_PUPTAKE'][:])}
    paths={'N':{'mycorrhizal':clean(h0['NPP_NACTIVE'][:]),'direct root':clean(h0['NPP_NNONMYC'][:]),'retranslocation':clean(h0['NPP_NRETRANS'][:]),'fixation':clean(h0['NPP_NFIX'][:])},
           'P':{'mycorrhizal':clean(h0['NPP_PACTIVE'][:]),'direct root':clean(h0['NPP_PNONMYC'][:]),'retranslocation':clean(h0['NPP_PRETRANS'][:])}}
    out={}
    for nut in ('N','P'):
        out[nut]={}
        for bname,pfts in BIOMES:
            W=np.zeros(A.shape); T=np.zeros(A.shape)
            for p in pfts: W+=wt[p]*A; T+=np.nan_to_num(tot[nut][p])*A
            ok=W>0; per=np.where(ok,T/np.where(ok,W,1),np.nan)*spy; mean=np.nansum(per*W)/W[ok].sum(); sd=np.sqrt(np.nansum(W*(np.nan_to_num(per)-mean)**2)/W[ok].sum())
            cells=np.isin(dom,pfts)&(lf>0.05); sh={k:float(np.nansum(np.nan_to_num(v)[cells]*A[cells])) for k,v in paths[nut].items()}; s=sum(sh.values())
            out[nut][bname]={'mean':mean,'sd':sd,'sum_TgC':T.sum()*spy/1e12,'shares':{k:100*v/s if s>0 else np.nan for k,v in sh.items()},'ncells':int(cells.sum())}
    return out
S={l:stats(l) for l in labels}; nb=len(labels)
fig,ax=plt.subplots(2,2,figsize=(6.5*nb+3,9)); x=np.arange(len(BIOMES)); wdt=0.8/nb
for r,nut in enumerate(('N','P')):
    for j,l in enumerate(labels):
        m=[S[l][nut][b]['mean'] for b,_ in BIOMES]; s=[S[l][nut][b]['sd'] for b,_ in BIOMES]
        ax[r,0].bar(x+(j-(nb-1)/2)*wdt,m,wdt*0.92,yerr=s,capsize=2,color=COLS[j%4],label=l,error_kw=dict(lw=0.8,ecolor='#555'))
    ax[r,0].set_ylabel(f'C used for {nut} acquisition\n(g C m$^{{-2}}$ of PFT area yr$^{{-1}}$, mean ± 1 SD)'); ax[r,0].set_xticks(x); ax[r,0].set_xticklabels([b.replace(' forest','\nforest') for b,_ in BIOMES],fontsize=8); ax[r,0].legend(fontsize=8,frameon=False); ax[r,0].grid(axis='y',alpha=.3)
    keys=list(S[labels[0]][nut][BIOMES[0][0]]['shares'].keys()); xx=np.concatenate([x+(j-(nb-1)/2)*wdt for j in range(nb)]); bottom=np.zeros(len(xx))
    for ki,k in enumerate(keys):
        vals=np.nan_to_num(np.concatenate([[S[l][nut][b]['shares'][k] for b,_ in BIOMES] for l in labels])); ax[r,1].bar(xx,vals,wdt*0.92,bottom=bottom,color=COLS[ki%4],label=k,edgecolor='white',lw=0.5); bottom+=vals
    ax[r,1].set_ylabel(f'share of C spent on {nut} acquisition (%)\n[cells by dominant PFT]'); ax[r,1].set_xticks(x); ax[r,1].set_xticklabels([b.replace(' forest','\nforest') for b,_ in BIOMES],fontsize=8); ax[r,1].set_ylim(0,100); ax[r,1].legend(fontsize=8,frameon=False,ncol=2,loc='lower right')
fig.suptitle(f'Braghiere et al. (2022) Figure 8 redrawn — {period} means; within each biome, bars are ordered as the left legend ({", ".join(labels)})',fontsize=10); plt.tight_layout(rect=(0,0,1,0.96))
out=f'/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/fig8_{period}_'+'_'.join(labels)+'.png'; plt.savefig(out,dpi=120); print('   wrote',out)
for l in labels:
    print(f'   {l}:')
    for nut in ('N','P'):
        for b,_ in BIOMES: v=S[l][nut][b]; print(f"      {nut} {b:28s} {v['mean']:7.1f} ± {v['sd']:6.1f} g C m-2 yr-1 | biome total {v['sum_TgC']:7.1f} Tg C/yr | shares: "+' '.join(f"{k} {s:4.0f}%" for k,s in v['shares'].items())+f" ({v['ncells']} cells)")
