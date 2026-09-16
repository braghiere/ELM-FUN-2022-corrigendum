#!/usr/bin/env python3
"""Control vs corrected (vs published 2022 product) — global and biome summaries, differences, figures, markdown report.
Usage: analyze_chains.py <label:h0path> [<label:h0path> ...]  (first = control). Uses last 120 months of each file.
Example: analyze_chains.py control:/.../corr22ctl_..._ICB20TRCNPRDCTCBC.clm2.h0.*.nc AB:/... ABC:/... published:/home/braghiere/ELM_FUN_output/ELM_FUNP/ELM_FUNP.clm2.h0.185001-201012.nc"""
import sys, glob, json, numpy as np, netCDF4 as nc, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
YR=3.15576e7; OUT='/home/braghiere/ELM-FUN-2022-corrigendum/analysis'
def load(path):
    fs=sorted(glob.glob(path)); assert fs, path
    if len(fs)==1: return nc.MFDataset(fs) if False else nc.Dataset(fs[0])
    return nc.MFDataset(fs)
def series(ds,n,sl):
    v=ds.variables[n][sl]; return np.ma.masked_invalid(np.asarray(v,dtype=float))
def summarize(ds,label):
    V=ds.variables; nt=V['time'].shape[0]; sl=slice(max(0,nt-120),nt)
    lat=V['lat'][:]; w=np.ma.masked_invalid(V['area'][:].astype(float)*V['landfrac'][:].astype(float))
    L=np.broadcast_to(lat[:,None],w.shape)
    def m(n): return series(ds,n,sl).mean(axis=0) if n in V else None
    def tsum(n): return series(ds,n,sl).sum(axis=0) if n in V else None
    def gm(a,mask=None):
        if a is None: return np.nan
        a=np.ma.masked_invalid(a); ww=w.copy()
        if mask is not None: ww=np.ma.masked_where(~mask,ww)
        ww=np.ma.masked_where(np.ma.getmaskarray(a),ww); s=float(ww.sum()); return float((a*ww).sum()/s) if s>0 else np.nan
    def gs(a,mask=None):
        if a is None: return np.nan
        a=np.ma.masked_invalid(a); ww=w.copy()
        if mask is not None: ww=np.ma.masked_where(~mask,ww)
        ww=np.ma.masked_where(np.ma.getmaskarray(a),ww); return float((a*ww).sum())
    F={'NPP':m('NPP'),'GPP':m('GPP'),'TOTVEGC':m('TOTVEGC'),'TOTSOMC':m('TOTSOMC'),'TOTECOSYSC':m('TOTECOSYSC'),'TOTVEGN':m('TOTVEGN'),'SMINN':m('SMINN'),
       'myc':m('NPP_NACTIVE'),'non':m('NPP_NNONMYC'),'fix':m('NPP_NFIX'),'nup':m('NPP_NUPTAKE'),'pmyc':m('NPP_PACTIVE'),'pnon':m('NPP_PNONMYC'),'pup':m('NPP_PUPTAKE'),
       'nam':m('NPP_NAM'),'necm':m('NPP_NECM'),'nfix':m('NFIX') if 'NFIX' in V else m('NFIX_TO_SMINN'),'ffix':m('FFIX_TO_SMINN'),
       'sumCfix':tsum('NPP_NFIX'),'sumNfix':tsum('NFIX') if 'NFIX' in V else tsum('NFIX_TO_SMINN')}
    bands={'GLOBAL':None,'BOREAL >50N':L>50,'TEMPERATE 30-50N':(L>30)&(L<=50),'TROPICS 23S-23N':(L>=-23)&(L<=23)}
    R={}
    for b,mask in bands.items():
        r={}
        r['NPP gC/m2/yr']=gm(F['NPP'],mask)*YR; r['GPP gC/m2/yr']=gm(F['GPP'],mask)*YR
        r['TOTVEGC kgC/m2']=gm(F['TOTVEGC'],mask)/1000; r['TOTSOMC kgC/m2']=gm(F['TOTSOMC'],mask)/1000; r['TOTECOSYSC kgC/m2']=gm(F['TOTECOSYSC'],mask)/1000
        r['TOTVEGN gN/m2']=gm(F['TOTVEGN'],mask); r['SMINN gN/m2']=gm(F['SMINN'],mask)
        T=gm(F['nup'],mask); r['myc %N-acq C']=100*gm(F['myc'],mask)/T; r['nonmyc %N-acq C']=100*gm(F['non'],mask)/T; r['fix %N-acq C']=100*gm(F['fix'],mask)/T
        A,E=gm(F['nam'],mask),gm(F['necm'],mask); r['AM share of myc N-C %']=100*A/(A+E) if (A+E)>0 else np.nan
        PT=gm(F['pmyc'],mask)+gm(F['pnon'],mask); r['P myc %P-acq C']=100*gm(F['pmyc'],mask)/PT if PT>0 else np.nan
        mycC=gm(F['myc'],mask)+gm(F['pmyc'],mask); gross=gm(F['NPP'],mask)+gm(F['nup'],mask)+gm(F['pup'],mask)
        r['myc C gC/m2/yr']=mycC*YR; r['myc C % gross prod']=100*mycC/gross; r['FUN cost % gross prod']=100*(gm(F['nup'],mask)+gm(F['pup'],mask))/gross
        r['symbiotic NFIX kgN/ha/yr']=gm(F['nfix'],mask)*YR*10; r['free-living FFIX kgN/ha/yr']=gm(F['ffix'],mask)*YR*10
        C,N=gs(F['sumCfix'],mask),gs(F['sumNfix'],mask); r['realized fix cost gC/gN']=C/N if N>0 else np.nan
        R[b]=r
    return R, {'npp':F['NPP'],'mycfrac':(F['myc']+F['pmyc'])/np.ma.masked_where(F['NPP']*YR<100,F['NPP']+F['nup']+F['pup']),'nfix':F['nfix'],'lat':lat,'lon':V['lon'][:]}
runs=[a.split(':',1) for a in sys.argv[1:]]; res={}; maps={}
for lab,path in runs:
    ds=load(path); res[lab],maps[lab]=summarize(ds,lab); print('summarized',lab)
json.dump(res,open(f'{OUT}/chain_summary.json','w'),indent=1)
labs=[l for l,_ in runs]; ctl=labs[0]
md=[f'# Control vs corrected — last decade of transient (area-weighted)\n\nRuns: {", ".join(labs)}. Differences are relative to `{ctl}`.\n']
for b in res[ctl]:
    md.append(f'\n## {b}\n\n| quantity | '+' | '.join(labs)+' | '+' | '.join(f'Δ {l}−{ctl}' for l in labs[1:])+' |\n|---|'+'---|'*(2*len(labs)-1))
    for q in res[ctl][b]:
        vals=[res[l][b].get(q,np.nan) for l in labs]; d=[v-vals[0] for v in vals[1:]]
        md.append(f'| {q} | '+' | '.join(f'{v:.3g}' for v in vals)+' | '+' | '.join(f'{x:+.3g}' for x in d)+' |')
open(f'{OUT}/CHAIN_REPORT.md','w').write('\n'.join(md)); print('wrote',f'{OUT}/CHAIN_REPORT.md')
# figures: biome bars of N-acq partition + symbiotic NFIX; maps of Δ myc fraction and Δ NPP for first corrected chain
fig,ax=plt.subplots(1,3,figsize=(16,4.5)); bands=list(res[ctl].keys()); x=np.arange(len(bands)); wd=0.8/len(labs)
for k,(q,t) in enumerate([('myc %N-acq C','mycorrhizal share of N-acquisition C (%)'),('symbiotic NFIX kgN/ha/yr','symbiotic BNF (kg N/ha/yr)'),('myc C % gross prod','mycorrhizal C, % of gross production')]):
    for i,l in enumerate(labs): ax[k].bar(x+(i-len(labs)/2+0.5)*wd,[res[l][b][q] for b in bands],wd,label=l)
    ax[k].set_xticks(x); ax[k].set_xticklabels([b.split()[0] for b in bands],fontsize=8); ax[k].set_title(t,fontsize=10); ax[k].grid(alpha=.3,axis='y')
ax[0].legend(fontsize=8); plt.tight_layout(); plt.savefig(f'{OUT}/figs/chains_biome_bars.png',dpi=130); print('wrote figs/chains_biome_bars.png')
if len(labs)>1:
    l1=labs[1]; fig,ax=plt.subplots(1,2,figsize=(14,4.5))
    d1=(maps[l1]['mycfrac']-maps[ctl]['mycfrac'])*100; d2=(maps[l1]['npp']-maps[ctl]['npp'])*YR
    for a,d,t,vm in [(ax[0],d1,f'Δ mycorrhizal C fraction of gross prod (%), {l1}−{ctl}',20),(ax[1],d2,f'Δ NPP (gC/m2/yr), {l1}−{ctl}',100)]:
        im=a.pcolormesh(maps[ctl]['lon'],maps[ctl]['lat'],d,cmap='RdBu_r',vmin=-vm,vmax=vm,shading='auto'); a.set_title(t,fontsize=10); plt.colorbar(im,ax=a,shrink=.8)
    plt.tight_layout(); plt.savefig(f'{OUT}/figs/chains_maps_delta.png',dpi=130); print('wrote figs/chains_maps_delta.png')
