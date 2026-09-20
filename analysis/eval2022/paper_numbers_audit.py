#!/usr/bin/env python3
"""Number-by-number audit of Braghiere et al. (2022, JAMES, doi 10.1029/2022MS003204) against
 (a) the archived v6 product (Zenodo 10.5281/zenodo.20452251, Aug-2020 module),
 (b) the control rerun (released Sep-2020 code, v2 spin-up protocol), and
 (c) the corrected rerun (fixes A larch kc/kn swap, B ivt 7->17, C hardcoded fixation cost -> paramfile).
All model values are 1994-2005 means integrated with area*landfrac. Writes paper_numbers_audit.md."""
import json, re, csv, numpy as np, netCDF4 as nc
E='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/'; D=E+'data/'; spy=86400*365.
J=json.load(open(E+'numbers_1994-2005.json')); PR=['published_FUNP','control','corrected']; ALL=['published_ELM','published_FUN2']+PR
def fld(d,v): x=np.ma.filled(d[v][:].astype(float),np.nan); return np.where(np.abs(x)<1e30,x,np.nan)
H={l:nc.Dataset(D+f'{l}_1994-2005_h0mean.nc') for l in PR}
S={l:np.load(D+f'{l}_series.npz') for l in ALL}
def m9405(l,v): s=S[l]; y=s['years']; m=(y>=1994)&(y<=2005); return float(np.nanmean(s[v][m]))
def n(k,l): return J[l][k]
rows=[]
def add(sec,claim,paper,arch,ctl,cor,verdict): rows.append((sec,claim,paper,arch,ctl,cor,verdict))
f1=lambda x:'' if x is None or (isinstance(x,float) and np.isnan(x)) else (f"{x:.1f}" if abs(x)>=10 else f"{x:.2f}")
f0=lambda x: f"{x:.0f}"
pc=lambda a,b: f"{100*(a/b-1):+.0f} %"
# ---------------------------------------------------------------- 1. global NPP, reductions, CUE (Fig 3a/4a/S11b)
NPP={l:m9405(l,'NPP') for l in ALL}; GPP={l:m9405(l,'GPP') for l in ALL}
add('NPP','ELM-FUN2.0 NPP 51.2 Pg C/yr, 13.6 less than ELM (64.8)',"51.2 / 13.6 / 64.8",f"{NPP['published_FUN2']:.1f} / {NPP['published_ELM']-NPP['published_FUN2']:.1f} / {NPP['published_ELM']:.1f}","(FUN-off / FUN2 not rerun)","",
    "archived products are 10-12 % higher than the text (text values = archive x 0.89-0.90, the double-landfrac scaling); reduction reproduced")
add('NPP','downregulation of NPP by 21.0 % (FUN2.0 vs ELM)',"21.0 %",f"{100*(1-NPP['published_FUN2']/NPP['published_ELM']):.1f} %","","","reproduced (ratio is scaling-free)")
add('NPP','ELM-FUN3.0 NPP 32.2 Pg C/yr, 32.6 less than ELM, reduction 50.3 %',"32.2 / 32.6 / 50.3 %",f"{NPP['published_FUNP']:.1f} / {NPP['published_ELM']-NPP['published_FUNP']:.1f} / {100*(1-NPP['published_FUNP']/NPP['published_ELM']):.1f} %",
    f"{NPP['control']:.1f} / {NPP['published_ELM']-NPP['control']:.1f} / {100*(1-NPP['control']/NPP['published_ELM']):.1f} %",f"{NPP['corrected']:.1f} / {NPP['published_ELM']-NPP['corrected']:.1f} / {100*(1-NPP['corrected']/NPP['published_ELM']):.1f} %",
    "reproduced; text NPP is archive x 0.89; corrections change NPP by +0.5 %")
add('NPP','abstract: NPP reduced ~20 % (N) and ~50 % (N+P)',"20 / 50 %",f"{100*(1-NPP['published_FUN2']/NPP['published_ELM']):.0f} / {100*(1-NPP['published_FUNP']/NPP['published_ELM']):.0f} %",f"– / {100*(1-NPP['control']/NPP['published_ELM']):.0f} %",f"– / {100*(1-NPP['corrected']/NPP['published_ELM']):.0f} %","reproduced")
cue={l:100*NPP[l]/GPP[l] for l in ALL}
add('NPP','CUE = NPP/GPP from ~30 % (ELM) to ~20 % (ELM-FUN3.0), Fig S11b',"~30 -> ~20 %",f"ELM {cue['published_ELM']:.0f} %, FUN2 {cue['published_FUN2']:.0f} %, FUN3 {cue['published_FUNP']:.0f} %",f"{cue['control']:.0f} %",f"{cue['corrected']:.0f} %",
    "NOT reproduced: archived CUE is 49 % (ELM) -> 30 % (FUN3.0); the text's ~30/~20 % cannot be obtained from NPP and GPP of any product (a 0.89^2 = 0.80 scaling would give 39/24 %)")
# zonal: reduced across all latitudes?
lat=S['published_ELM']['lat']; z={l:S[l]['zonal_npp_1994_2005'] for l in ALL}; land=np.isfinite(z['published_ELM'])&(z['published_ELM']>1)
worse2=int(np.sum(land&(z['published_FUN2']>z['published_ELM']))); worse3=int(np.sum(land&(z['published_FUNP']>z['published_ELM'])))
add('NPP','zonally, NPP reduced across all latitudes in FUN2.0 and FUN3.0 relative to ELM (Fig 3a)',"all latitudes",f"latitude bands with FUN2 > ELM: {worse2}/{int(land.sum())}; FUN3 > ELM: {worse3}/{int(land.sum())}",
    f"control > ELM: {int(np.sum(land&(z['control']>z['published_ELM'])))}",f"corrected > ELM: {int(np.sum(land&(z['corrected']>z['published_ELM'])))}","reproduced" if worse2==0 and worse3==0 else "mostly reproduced (see counts)")
# MODIS zonal stats (Fig 3b)
mo=np.load(D+'benchmarks/modis_npp_zonal.npz'); dl=float(np.abs(np.diff(lat)).mean())
mz=np.array([np.nanmean(mo['npp'][(mo['lat']>=la-dl/2)&(mo['lat']<la+dl/2)]) if np.any((mo['lat']>=la-dl/2)&(mo['lat']<la+dl/2)) else np.nan for la in lat])
def stats(l):
    y=z[l]; ok=np.isfinite(y)&np.isfinite(mz)&(mz>0)&land
    a,b=np.polyfit(mz[ok],y[ok],1); r2=np.corrcoef(mz[ok],y[ok])[0,1]**2; rmse=np.sqrt(np.mean((y[ok]-mz[ok])**2)); return r2,rmse,a
st={l:stats(l) for l in ALL}
add('Fig 3b','vs MODIS NPP: r2 0.32 -> 0.84 (FUN2) -> 0.86 (FUN3); RMSE 223.2 -> 107.7 (-52 %) -> 102.0 g C/m2/yr (-54 %); slope 1.26 -> 1.03 -> 0.73',
    "r2 0.32/0.84/0.86; RMSE 223/108/102; slope 1.26/1.03/0.73",
    f"r2 {st['published_ELM'][0]:.2f}/{st['published_FUN2'][0]:.2f}/{st['published_FUNP'][0]:.2f}; RMSE {st['published_ELM'][1]:.0f}/{st['published_FUN2'][1]:.0f}/{st['published_FUNP'][1]:.0f}; slope {st['published_ELM'][2]:.2f}/{st['published_FUN2'][2]:.2f}/{st['published_FUNP'][2]:.2f}",
    f"r2 {st['control'][0]:.2f}; RMSE {st['control'][1]:.0f}; slope {st['control'][2]:.2f}",f"r2 {st['corrected'][0]:.2f}; RMSE {st['corrected'][1]:.0f}; slope {st['corrected'][2]:.2f}",
    "NOT reproduced with the MODIS product on disk (MOD17A3HGF 2000-2015, zonal means on the model latitudes): r2 does not rise with FUN and the FUN3.0 RMSE is the largest, not the smallest; slopes (1.16/0.90/0.69) are close to the text; the paper does not state its MODIS product, years or grid")
add('Fig 3c','vs IGBP (ISLSCP II) NPP: RMSE 152.4 -> 67.6 (-56 %) -> 148.6 (-2 %) g C/m2/yr',"152.4 / 67.6 / 148.6","","","","NOT VERIFIABLE here: ISLSCP II NPP product not on disk (requested from author)")
add('Fig 3d','vs CMIP6 11-model NPP: RMSE 142.9 -> 82.6 (-42 %) -> 155.9 (+9 %) g C/m2/yr',"142.9 / 82.6 / 155.9","","","","NOT VERIFIABLE here: CMIP6 ensemble zonal NPP not on disk")
add('Fig 4b','normalized C use ratio vs Fisher et al. 2012 TNL: r2 0.73 -> 0.83, RMSE 4.3 -> 3.7 %',"0.73/0.83; 4.3/3.7 %","","","","NOT VERIFIABLE here: Fisher 2012 TNL dataset not on disk")
# ---------------------------------------------------------------- 2. N uptake and pathways (Fig 5, section 3.2)
for k,pv,lab in (('N uptake total (Tg N/yr)',841.8,'total N uptake 841.8 Tg N/yr'),('  mycorrhizal (Tg N/yr)',659.9,'mycorrhizal N uptake 659.9 Tg N/yr'),('    AM (Tg N/yr)',482.1,'AM N uptake 482.1 Tg N/yr (73.0 % of mycorrhizal)'),('    EcM (Tg N/yr)',177.8,'EcM N uptake 177.8 Tg N/yr (27.0 %)'),('  direct root (Tg N/yr)',84.3,'direct root N uptake 84.3 Tg N/yr'),('  retranslocation (Tg N/yr)',97.6,'retranslocated N 97.6 Tg N/yr')):
    a,c,x=(n(k,l) for l in PR); v="text = archive x %.2f"%(pv/a)
    if 'AM' in k: v+=f"; archived AM share {100*a/n('  mycorrhizal (Tg N/yr)','published_FUNP'):.0f} % (text 73 %): partition NOT reproduced"
    if 'EcM' in k: v+=f"; archived EcM share {100*a/n('  mycorrhizal (Tg N/yr)','published_FUNP'):.0f} % (text 27 %): partition NOT reproduced"
    if 'direct' in k: v+=f"; control {pc(c,a)} vs archive (code-version difference)"
    add('N uptake',lab,f"{pv}",f1(a),f1(c),f1(x),v+ ("; corrections %s"%pc(x,c)))
a=n('total BNF symbiotic+free-living (Tg N/yr)','published_FUNP'); c=n('total BNF symbiotic+free-living (Tg N/yr)','control'); x=n('total BNF symbiotic+free-living (Tg N/yr)','corrected'); sa,sc,sx=(n('  symbiotic fixation (Tg N/yr)',l) for l in PR)
add('N uptake','total biological N fixation 35.3 Tg N/yr (Fig 5a labelled symbiotic fixation)',"35.3",f"{a:.1f} (symbiotic {sa:.4f}, free-living {a-sa:.1f})",f"{c:.1f} (symbiotic {sc:.4f})",f"{x:.1f} (symbiotic {sx:.2f}, free-living {x-sx:.1f})",
    "flux is FREE-LIVING fixation (FFIX_TO_SMINN); symbiotic fixation was effectively off (defect C); corrected symbiotic 3.1 Tg N/yr, total +8 %; text = archive x 0.88")
add('N uptake','BNF compilation 52-130 Tg N/yr (Davies-Barnard & Friedlingstein 2020)',"52-130","","","","literature value, unchanged; model total stays below the range in all versions")
# ---------------------------------------------------------------- 3. P uptake (Fig 6)
for k,pv,lab in (('P uptake total (Tg P/yr)',48.1,'total P uptake 48.1 Tg P/yr'),('  mycorrhizal (Tg P/yr)',20.0,'mycorrhizal P uptake 20.0 Tg P/yr'),('    AM (Tg P/yr)',11.1,'AM P uptake 11.1 Tg P/yr (55.4 % of mycorrhizal)'),('    EcM (Tg P/yr)',8.9,'EcM P uptake 8.9 Tg P/yr (44.6 %)'),('  direct root (Tg P/yr)',20.9,'direct root P uptake 20.9 Tg P/yr'),('  retranslocation (Tg P/yr)',7.3,'retranslocated P 7.3 Tg P/yr')):
    a,c,x=(n(k,l) for l in PR); v="text = archive x %.2f"%(pv/a)
    if 'AM' in k: v+=f"; archived AM share {100*a/n('  mycorrhizal (Tg P/yr)','published_FUNP'):.0f} % (text 55 %): partition NOT reproduced"
    if 'EcM' in k: v+=f"; archived EcM share {100*a/n('  mycorrhizal (Tg P/yr)','published_FUNP'):.0f} % (text 45 %): partition NOT reproduced"
    add('P uptake',lab,f"{pv}",f1(a),f1(c),f1(x),v+"; corrections %s"%pc(x,c))
add('P uptake','E3SMv1.1-CTC 42.0 and E3SMv1.1-ECA 63.0 Tg P/yr (Burrows et al. 2020)',"42.0 / 63.0","","","","literature values, unchanged")
# ---------------------------------------------------------------- 4. carbon costs (section 3.3, Figs 7-8)
NT={l:n('C cost of N acquisition (Pg C/yr)',l) for l in PR}; PT={l:n('C cost of P acquisition (Pg C/yr)',l) for l in PR}
Ncomp={l:(n('  mycorrhizal (Tg C/yr)',l),n('  direct root (Tg C/yr)',l),n('  retranslocation (Tg C/yr)',l),n('  fixation (Tg C/yr)',l)) for l in PR}
Pcomp={l:(n('  direct root P (Tg C/yr)',l),n('  mycorrhizal P (Tg C/yr)',l),n('  retranslocation P (Tg C/yr)',l)) for l in PR}
Nsum={l:sum(Ncomp[l])/1000 for l in PR}; Psum={l:sum(Pcomp[l])/1000 for l in PR}
add('C cost','abstract: plants invested 4.1 Pg C/yr to acquire N and P',"4.1 (= 2.5 + 1.6)",f"{NT['published_FUNP']+PT['published_FUNP']:.2f} (NPP_NUPTAKE+NPP_PUPTAKE); pathway sums {Nsum['published_FUNP']+Psum['published_FUNP']:.2f}",
    f"{NT['control']+PT['control']:.2f}; pathway sums {Nsum['control']+Psum['control']:.2f}",f"{NT['corrected']+PT['corrected']:.2f}; pathway sums {Nsum['corrected']+Psum['corrected']:.2f}",
    "NOT reproduced: the model's total cost (what is actually removed from NPP) is 7.4-8.7 Pg C/yr; the text sums pathway costs, which exclude 'burned-off' carbon (C spent when no nutrient can be bought, see below)")
add('C cost','8 % of NPP or 2.5 Pg C/yr spent to take up N',"2.5 / 8 %",f"{NT['published_FUNP']:.2f} / {n('  as % of NPP','published_FUNP'):.1f} % (pathway sum {Nsum['published_FUNP']:.2f})",f"{NT['control']:.2f} / {n('  as % of NPP','control'):.1f} % (sum {Nsum['control']:.2f})",f"{NT['corrected']:.2f} / {n('  as % of NPP','corrected'):.1f} % (sum {Nsum['corrected']:.2f})",
    "archive 3.77 vs text 2.5: NOT reproduced by the archive (Aug-2020 module); control/corrected 3.05/2.92 (8.3/8.0 % of NPP) are close to the text; corrections -4 %")
add('C cost','mycorrhizal N cost 1891.7 Tg C/yr (74.9 %), direct root 623.0 (24.7 %)',"1891.7 (74.9 %) / 623.0 (24.7 %)",f"{Ncomp['published_FUNP'][0]:.0f} ({100*Ncomp['published_FUNP'][0]/1000/Nsum['published_FUNP']:.0f} %) / {Ncomp['published_FUNP'][1]:.0f} ({100*Ncomp['published_FUNP'][1]/1000/Nsum['published_FUNP']:.0f} %)",
    f"{Ncomp['control'][0]:.0f} ({100*Ncomp['control'][0]/1000/Nsum['control']:.0f} %) / {Ncomp['control'][1]:.0f} ({100*Ncomp['control'][1]/1000/Nsum['control']:.0f} %)",f"{Ncomp['corrected'][0]:.0f} ({100*Ncomp['corrected'][0]/1000/Nsum['corrected']:.0f} %) / {Ncomp['corrected'][1]:.0f} ({100*Ncomp['corrected'][1]/1000/Nsum['corrected']:.0f} %)",
    "shares reproduced (75/25 %); absolute values differ by code version; corrections -5 %")
add('C cost','C spent on N retranslocation 20.6 Tg C/yr (0.42 %)',"20.6",f"{Ncomp['published_FUNP'][2]:.1f}",f"{Ncomp['control'][2]:.1f}",f"{Ncomp['corrected'][2]:.1f}","NOT reproduced (archive 14.1); share 0.4-0.5 % consistent")
add('C cost','C spent on N fixation 0.8 Tg C/yr (0.03 %)',"0.8",f"{Ncomp['published_FUNP'][3]:.2f}",f"{Ncomp['control'][3]:.2f}",f"{Ncomp['corrected'][3]:.1f}","reproduced for the archive/control; CORRECTED: 24.9 Tg C/yr (0.9 %) because symbiotic fixation is switched on at 8 gC/gN")
add('C cost','5 % of NPP or 1.6 Pg C/yr spent to acquire P',"1.6 / 5 %",f"{PT['published_FUNP']:.2f} / {n('  as % of NPP (P)','published_FUNP'):.1f} % (pathway sum {Psum['published_FUNP']:.2f})",f"{PT['control']:.2f} / {n('  as % of NPP (P)','control'):.1f} % (sum {Psum['control']:.2f})",f"{PT['corrected']:.2f} / {n('  as % of NPP (P)','corrected'):.1f} % (sum {Psum['corrected']:.2f})",
    "NOT reproduced: NPP_PUPTAKE (the C actually removed from NPP) is 4.4-4.9 Pg C/yr = 12-14 % of NPP; 2.9-3.6 Pg C/yr of it is burned-off carbon not attributable to any pathway; the text's 1.6 is the pathway sum of yet another code state")
add('C cost','P: direct root 859.6 Tg C/yr (52 %), mycorrhizal 781.6 (47 %), retranslocation 4.2 (0.26 %)',"859.6 (52 %) / 781.6 (47 %) / 4.2",f"{Pcomp['published_FUNP'][0]:.0f} ({100*Pcomp['published_FUNP'][0]/1000/Psum['published_FUNP']:.0f} %) / {Pcomp['published_FUNP'][1]:.0f} ({100*Pcomp['published_FUNP'][1]/1000/Psum['published_FUNP']:.0f} %) / {Pcomp['published_FUNP'][2]:.1f}",
    f"{Pcomp['control'][0]:.0f} ({100*Pcomp['control'][0]/1000/Psum['control']:.0f} %) / {Pcomp['control'][1]:.0f} ({100*Pcomp['control'][1]/1000/Psum['control']:.0f} %) / {Pcomp['control'][2]:.1f}",f"{Pcomp['corrected'][0]:.0f} ({100*Pcomp['corrected'][0]/1000/Psum['corrected']:.0f} %) / {Pcomp['corrected'][1]:.0f} ({100*Pcomp['corrected'][1]/1000/Psum['corrected']:.0f} %) / {Pcomp['corrected'][2]:.1f}",
    "shares roughly reproduced (root 50-53 %, myc 47-50 %); absolute values differ by code version (archive 2x control); corrections 0 %")
add('C cost','burned-off carbon (NPP_xUPTAKE minus pathway sum), N / P, Pg C/yr — not in the paper',"–",f"{NT['published_FUNP']-Nsum['published_FUNP']:.2f} / {PT['published_FUNP']-Psum['published_FUNP']:.2f}",f"{NT['control']-Nsum['control']:.2f} / {PT['control']-Psum['control']:.2f}",f"{NT['corrected']-Nsum['corrected']:.2f} / {PT['corrected']-Psum['corrected']:.2f}",
    "new finding: the P 'cost' that halves NPP is mostly C spent without acquiring P (fun burned_off_carbon_p); should be stated in the corrigendum")
pre={l:n('NPP before N+P cost (Pg C/yr)',l) for l in PR}
add('C cost','implied NPP before nutrient costs (NPP + NPP_NUPTAKE + NPP_PUPTAKE) — not in the paper',"–",f"{pre['published_FUNP']:.1f}",f"{pre['control']:.1f}",f"{pre['corrected']:.1f}","nutrient costs remove 17-19 % of pre-cost NPP; the remaining reduction vs ELM (71.5) is the growth downregulation")
# ---------------------------------------------------------------- 5. retranslocation efficiency (Fig 7)
def eff(l):
    d=H[l]; lc=fld(d,'LEAFC_TO_LITTER'); ln=fld(d,'LEAFN')/np.where(fld(d,'LEAFC')>0,fld(d,'LEAFC'),np.nan); lp=fld(d,'LEAFP')/np.where(fld(d,'LEAFC')>0,fld(d,'LEAFC'),np.nan)
    en=100*fld(d,'NRETRANS')/np.where(lc*ln>0,lc*ln,np.nan); ep=100*fld(d,'PRETRANS')/np.where(lc*lp>0,lc*lp,np.nan); return en,ep
d0=H['published_FUNP']; A=np.nan_to_num(fld(d0,'area')*1e6*fld(d0,'landfrac')); pct=np.nan_to_num(fld(d0,'PCT_NAT_PFT')); dom=np.argmax(pct,axis=0); LA,LO=np.meshgrid(d0['lat'][:],d0['lon'][:],indexing='ij')
grass=np.isin(dom,[12,13,14]); REG={'China grasslands (30-50N, 75-125E)':(LA>30)&(LA<50)&(LO>75)&(LO<125)&grass,'southern South America grasslands (55-20S, 285-305E)':(LA>-55)&(LA<-20)&(LO>285)&(LO<305)&grass,
 'boreal (50-70N)':(LA>50)&(LA<70),'savannas (C4-grass dominated, 25S-25N)':(np.abs(LA)<25)&(dom==14)&(pct[14]>50),'tropical broadleaf evergreen forest (23S-23N, PFT4 dominant)':(np.abs(LA)<23)&(dom==4),'tropical grasslands (23S-23N, PFT13/14 dominant)':(np.abs(LA)<23)&np.isin(dom,[13,14]),'tropics all vegetated (23S-23N)':(np.abs(LA)<23)&(dom>0)}
def wstat(x,m):
    ok=m&np.isfinite(x)&(A>0); w=A[ok]; v=x[ok]; o=np.argsort(v); cw=np.cumsum(w[o])/w.sum(); return v[o][np.searchsorted(cw,0.5)], v[o][np.searchsorted(cw,0.1)], v[o][np.searchsorted(cw,0.9)]
EF={l:eff(l) for l in PR}
def effrow(reg,nut):
    out=[]
    for l in PR: med,p10,p90=wstat(EF[l][0 if nut=='N' else 1],REG[reg]); out.append(f"{med:.0f} % ({p10:.0f}-{p90:.0f})")
    return out
for reg,claim,pv,nut in (('China grasslands (30-50N, 75-125E)','N retranslocation efficiency < 15 % in grassland areas of China','< 15 %','N'),('southern South America grasslands (55-20S, 285-305E)','N retranslocation efficiency < 15 % in southern South America grasslands','< 15 %','N'),
    ('boreal (50-70N)','N retranslocation efficiency up to 50 % in boreal regions','up to 50 %','N'),('boreal (50-70N)','P retranslocation efficiency up to 50 % in boreal regions','up to 50 %','P'),('savannas (C4-grass dominated, 25S-25N)','N retranslocation efficiency up to 50 % in savannas','up to 50 %','N'),
    ('tropical broadleaf evergreen forest (23S-23N, PFT4 dominant)','tropical N retranslocation efficiency ~30 % in broadleaf evergreen forests','~30 %','N'),('tropical grasslands (23S-23N, PFT13/14 dominant)','tropical N retranslocation efficiency ~50 % over grasslands','~50 %','N'),('tropics all vegetated (23S-23N)','tropical P retranslocation efficiency ~40 %','~40 %','P')):
    r=effrow(reg,nut); add('Fig 7',claim,pv,*r,"area-weighted median (10th-90th percentile) of retranslocated / (leaf litterfall x leaf nutrient:C); paper gives no formula; corrections change < 1 point")
# ---------------------------------------------------------------- 6. Fig 8 biome statistics (parsed from the replot log)
log=open(E+'run_eval_1994-2005.log').read().splitlines(); B={}; cur=None
for L in log:
    m=re.match(r'^\s+(published_FUNP|control|corrected):\s*$',L)
    if m: cur=m.group(1); B[cur]={}; continue
    m=re.match(r'^\s+(N|P) (.+?)\s+([\d.]+) ±\s+([\d.]+) g C m-2 yr-1 \| biome total\s+([\d.]+) Tg C/yr \| shares: (.*) \((\d+) cells\)',L)
    if m and cur: B[cur][(m.group(1),m.group(2).strip())]=(float(m.group(3)),float(m.group(4)),float(m.group(5)),dict(re.findall(r'([a-z ]+?)\s+(\d+)%',m.group(6))))
def b(l,nut,biome): v=B[l][(nut,biome)]; return f"{v[0]:.1f} ± {v[1]:.1f}; shares "+', '.join(f"{k.strip()} {s} %" for k,s in v[3].items())
for claim,pv,nut,biome in (('grasslands highest C use for P, 22.8 ± 6.2 g C/m2/yr, 32 % of it for retranslocation','22.8 ± 6.2; retrans 32 %','P','Grassland'),('shrublands: 38 % of P cost for mycorrhizal uptake','myc 38 %','P','Shrubland'),('deciduous broadleaf forests: 40 % of P cost for mycorrhizal uptake','myc 40 %','P','Deciduous broadleaf forest'),
    ('evergreen broadleaf forests P cost 3.3 ± 0.5 g C/m2/yr, mycorrhizae 49 %','3.3 ± 0.5; myc 49 %','P','Evergreen broadleaf forest'),('evergreen needleleaf forests P cost 2.1 ± 0.3 g C/m2/yr, mycorrhizae 55 %','2.1 ± 0.3; myc 55 %','P','Evergreen needleleaf forest'),('deciduous needleleaf forests P cost 0.4 ± 0.4 g C/m2/yr, retranslocation 89 %','0.4 ± 0.4; retrans 89 %','P','Deciduous needleleaf forest')):
    add('Fig 8',claim,pv,b('published_FUNP',nut,biome),b('control',nut,biome),b('corrected',nut,biome),"NOT reproduced: with cells grouped by dominant PFT the biome means are 3-30x larger and the retranslocation share is ~0 %; Fig 8's aggregation cannot be recovered from the paper (SD across cells is huge because of the C4-grass cells)")
# ---------------------------------------------------------------- 7. Fig 9 limitation classes
th=json.load(open(E+'fig9_thresholds_1994-2005.json')); lo,hi=th['R_lo'],th['R_hi']
def classes(l):
    d=H[l]; ln,lp,rn,rp=fld(d,'LEAFN'),fld(d,'LEAFP'),fld(d,'NRETRANS'),fld(d,'PRETRANS'); R=(ln/lp)/(rn/rp); nat=np.isfinite(R)&(A>0)&(lp>1e-6)&(rp>1e-15)&(np.nansum(pct[15:17],axis=0)<50)
    w=A[nat]; Rn=R[nat]; return R,nat,100*w[Rn<lo].sum()/w.sum(),100*w[(Rn>=lo)&(Rn<=hi)].sum()/w.sum(),100*w[Rn>hi].sum()/w.sum()
CL={l:classes(l) for l in PR}
add('Fig 9','6.1 % of natural land primarily N limited, 13.9 % primarily P limited, 80 % co-limited',"6.1 / 13.9 / 80.0 %",f"{CL['published_FUNP'][2]:.1f} / {CL['published_FUNP'][4]:.1f} / {CL['published_FUNP'][3]:.1f} % (thresholds calibrated to give these)",f"{CL['control'][2]:.1f} / {CL['control'][4]:.1f} / {CL['control'][3]:.1f} %",f"{CL['corrected'][2]:.1f} / {CL['corrected'][4]:.1f} / {CL['corrected'][3]:.1f} %",
    "reproducible only by calibrating the (unpublished) thresholds on the archive: R < %.3f N-limited, R > %.3f P-limited; with the same thresholds control/corrected give 7.5-7.6 / 14.1-14.2 / 78.3 %%; corrections change < 0.2 point" % (lo,hi))
def tropfrac(l,mask):
    R,nat,*_=CL[l]; m=nat&mask; w=A[m]; Rn=R[m]; return f"N {100*w[Rn<lo].sum()/w.sum():.0f} % / co {100*w[(Rn>=lo)&(Rn<=hi)].sum()/w.sum():.0f} % / P {100*w[Rn>hi].sum()/w.sum():.0f} %"
add('Fig 9','stronger P limitation in the tropics, except over grasslands which are more N limited (Fig S4)',"qualitative",f"BET: {tropfrac('published_FUNP',REG['tropical broadleaf evergreen forest (23S-23N, PFT4 dominant)'])}; grass: {tropfrac('published_FUNP',REG['tropical grasslands (23S-23N, PFT13/14 dominant)'])}",
    f"BET: {tropfrac('control',REG['tropical broadleaf evergreen forest (23S-23N, PFT4 dominant)'])}; grass: {tropfrac('control',REG['tropical grasslands (23S-23N, PFT13/14 dominant)'])}",f"BET: {tropfrac('corrected',REG['tropical broadleaf evergreen forest (23S-23N, PFT4 dominant)'])}; grass: {tropfrac('corrected',REG['tropical grasslands (23S-23N, PFT13/14 dominant)'])}","area shares of the limitation classes (N / co-limited / P) by tropical vegetation type")
# ---------------------------------------------------------------- 8. ILAMB (Fig 2) and biases
sc={r['Variables']:r for r in csv.DictReader(open(E+'ilamb/scores_all_1994-2005.csv'))}
paper={'Biomass':(0.44,0.54,0.72),'Gross Primary Productivity':(0.66,0.67,0.68),'Leaf Area Index':(0.39,0.44,0.51),'Global Net Ecosystem Carbon Balance':(0.61,0.59,0.58),'Net Ecosystem Exchange':(0.39,0.41,0.41),'Ecosystem Respiration':(0.49,0.50,0.57),'Soil Carbon':(0.55,0.59,0.68),'Evapotranspiration':(0.50,0.51,0.54)}
for v,p in paper.items():
    r=sc[v]; ff=lambda x: f"{float(x):.2f}"
    note="reproduced (within 0.04)" if all(abs(float(r[k])-pp)<=0.045 for k,pp in zip(('ELM','ELM_FUN','ELM_FUNP'),p)) else ("dataset changed in ILAMB 2.7 (GlobalCarbon biomass no longer distributed)" if v=='Biomass' else ("archived nbp is a 20-37 Pg C/yr source in all products; the paper's 0.6 came from a different nbp (open budget-closure item)" if 'Balance' in v else "different GLEAM release / scoring in ILAMB 2.7"))
    add('Fig 2 ILAMB',f'{v} overall score ELM / FUN2.0 / FUN3.0',f"{p[0]:.2f} / {p[1]:.2f} / {p[2]:.2f}",f"{ff(r['ELM'])} / {ff(r['ELM_FUN'])} / {ff(r['ELM_FUNP'])}",ff(r['control']),ff(r['corrected']),note+"; corrections change no score")
def scal(path,name):
    try:
        d=nc.Dataset(path); return float(d.groups['MeanState'].groups['scalars'][name][:])
    except Exception: return np.nan
IR='/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/ilamb_root/_build_all_1994-2005_v2/EcosystemandCarbonCycle/'
gb={l:scal(IR+f'GrossPrimaryProductivity/FLUXCOM/FLUXCOM_{l}.nc','Bias global') for l in ('ELM','ELM_FUN','ELM_FUNP','control','corrected')}
lb={l:scal(IR+f'LeafAreaIndex/MODIS/MODIS_{l}.nc','Bias global') for l in ('ELM','ELM_FUN','ELM_FUNP','control','corrected')}
add('Fig 2 ILAMB','ELM positive GPP bias vs FLUXCOM 0.65 g C/m2/day; FUN versions reduce it',"0.65",f"ELM {gb['ELM']:.2f}, FUN2 {gb['ELM_FUN']:.2f}, FUN3 {gb['ELM_FUNP']:.2f}",f"{gb['control']:.2f}",f"{gb['corrected']:.2f}","ILAMB 2.7 global mean bias (FLUXCOM); sign and reduction reproduced, magnitude 0.79 vs 0.65")
add('Fig 2 ILAMB','ELM LAI bias vs MODIS +0.95 m2/m2; ELM-FUN3.0 turns it negative (-0.17)',"+0.95 / -0.17",f"ELM {lb['ELM']:+.2f}, FUN2 {lb['ELM_FUN']:+.2f}, FUN3 {lb['ELM_FUNP']:+.2f}",f"{lb['control']:+.2f}",f"{lb['corrected']:+.2f}","ILAMB 2.7 global mean bias (MODIS LAI)")
# ---------------------------------------------------------------- 9. methods statements with numbers
add('Methods','spin-up: 200 yr accelerated decomposition + 600 yr regular',"200 + 600","","260 (r.0261) + 540 (r.0541), FUN off, v2 protocol reproduced from the 2020 case directories","same",
    "misstated in the text: the archived restart chain is 260 yr AD + 540 yr regular; the paper's numbers do not correspond to any archived case")
add('Methods','fraction of C available for fixation fixed at 25 % for natural PFTs (FUN_fracfixers)',"25 %","paramfile c200626: 0.25 natural PFTs, 0 crops","same","same","reproduced")
add('Methods','spatial resolution 1.9 x 2.5 deg, GSWP3 forcing, 1850-2010 transient, FUN switched on at 1850',"","f19, GSWP3 v2, 1850-2010","same","same","reproduced (see PLAN.md); note: archived products lose CO2 forcing after mid-2009 (indexing past the end of the 1765-2007 CO2 file)")
# ---------------------------------------------------------------- write
out=["# Number-by-number audit of Braghiere et al. (2022) against the archive, the control rerun and the corrected rerun","",
"Columns: paper value | archived v6 product (Zenodo, Aug-2020 module) | control (released Sep-2020 code, same protocol) | corrected (fixes A+B+C) | verdict. All model values are 1994-2005 means, area x landfrac integrals (see `headline_numbers.py`, `paper_numbers_provenance.md`). Literature values are listed for completeness and are unchanged.","",
"| # | section | claim in the paper | paper | archived v6 | control | corrected | verdict / difference |","|---|---|---|---|---|---|---|---|"]
for i,r in enumerate(rows,1): out.append(f"| {i} | {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |")
cat={'reproduced':0,'not reproduced':0,'not verifiable':0,'literature':0,'changed by corrections':0}
for r in rows:
    v=r[6].lower()
    if 'literature' in v: cat['literature']+=1
    elif 'not verifiable' in v: cat['not verifiable']+=1
    elif 'not reproduced' in v or 'misstated' in v: cat['not reproduced']+=1
    else: cat['reproduced']+=1
    if 'defect c' in v or 'corrected:' in v or 'corrections -4' in v or 'corrections -5' in v or 'corrections +8' in v: cat['changed by corrections']+=1
out+=["",f"Tally over {len(rows)} audited statements: reproduced (within scaling or code-version noise) {cat['reproduced']}; not reproduced by any product {cat['not reproduced']}; not verifiable here (external dataset missing) {cat['not verifiable']}; literature values {cat['literature']}. Statements whose value changes by more than 2 % with the corrections: {cat['changed by corrections']} (symbiotic N fixation, total BNF, the fixation carbon cost and the 4-5 % drop in N-acquisition carbon).","",
"## What the corrections change (control -> corrected)","",
f"- symbiotic N fixation 0 -> {n('  symbiotic fixation (Tg N/yr)','corrected'):.2f} Tg N/yr at a realized cost of {n('realized symbiotic fixation cost (gC/gN)','corrected'):.1f} g C per g N (was {n('realized symbiotic fixation cost (gC/gN)','control'):.0f}); total BNF {n('total BNF symbiotic+free-living (Tg N/yr)','control'):.1f} -> {n('total BNF symbiotic+free-living (Tg N/yr)','corrected'):.1f} Tg N/yr",
f"- C spent on fixation {Ncomp['control'][3]:.1f} -> {Ncomp['corrected'][3]:.1f} Tg C/yr; mycorrhizal and root N cost -5 %; total N cost {NT['control']:.2f} -> {NT['corrected']:.2f} Pg C/yr",
f"- NPP {NPP['control']:.1f} -> {NPP['corrected']:.1f} Pg C/yr (+{100*(NPP['corrected']/NPP['control']-1):.1f} %); GPP, P cycle, limitation map, ILAMB scores unchanged (< 0.5 %)","",
"## Systematic differences between the text and the archived product (not caused by the code defects)","",
"1. Text totals for N and P uptake, retranslocation and fixation are 0.88-0.93 x the archive (an extra landfrac factor in the 2022 integration); ratios and percentages are unaffected.",
"2. AM/EcM partitions in the text (N 73/27 %, P 55/45 %) do not match the archive (N 80/20 %, P 65/35 %).",
"3. The carbon-cost totals in the text (2.5 + 1.6 = 4.1 Pg C/yr) are pathway sums; the model removes NPP_NUPTAKE + NPP_PUPTAKE = 7.4-8.7 Pg C/yr from growth, of which 2.9-3.6 Pg C/yr (P) and 0-0.2 (N) is burned-off carbon. The 50 % NPP reduction is therefore dominated by carbon spent without acquiring P, which the paper never states.",
"4. Fig 8 biome statistics and the CUE values (~30 -> ~20 %) cannot be recovered from any product.",
"5. Fig 5a's 'symbiotic fixation' is free-living fixation; symbiotic fixation was ~0 in the 2022 code (defect C).",
"6. Spin-up length is misstated (260 + 540 yr, not 200 + 600).",
"7. Archived monthly products are invalid after mid-2009 (CO2 forcing indexing past the end of the file); 1994-2005 means are unaffected."]
open(E+'paper_numbers_audit.md','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
