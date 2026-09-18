#!/usr/bin/env python3
"""Headline numbers of Braghiere et al. (2022), recomputed side by side for several runs from *_h0mean.nc files.
Usage: numbers.py <period e.g. 1994-2005> <label1> [<label2> ...]   (labels = prefixes of data/<label>_<period>_h0mean.nc)
Definitions follow the paper: totals are area-weighted global sums (area*landfrac); C costs 'of NPP' use the reported NPP
(the paper: 2.5 Pg C/yr = 8 % of 32.2 Pg C/yr); total BNF = symbiotic (NFIX) + free-living (FFIX_TO_SMINN); CUE = NPP/GPP.
Writes numbers_<period>.md (markdown) and numbers_<period>.json."""
import sys, json, numpy as np, netCDF4 as nc
period=sys.argv[1]; labels=sys.argv[2:]; D='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/'
spy=86400*365.
paper={'N uptake total (Tg N/yr)':841.8,'  mycorrhizal (Tg N/yr)':659.9,'    AM (Tg N/yr)':482.1,'    EcM (Tg N/yr)':177.8,'  direct root (Tg N/yr)':84.3,'  retranslocation (Tg N/yr)':97.6,'  symbiotic fixation (Tg N/yr)':None,
       'total BNF symbiotic+free-living (Tg N/yr)':35.3,'P uptake total (Tg P/yr)':48.1,'  mycorrhizal (Tg P/yr)':20.0,'    AM (Tg P/yr)':11.1,'    EcM (Tg P/yr)':8.9,'  direct root (Tg P/yr)':20.9,'  retranslocation (Tg P/yr)':7.3,
       'C cost of N acquisition (Pg C/yr)':2.5,'  as % of NPP':8.0,'  mycorrhizal (Tg C/yr)':1891.7,'  direct root (Tg C/yr)':623.0,'  retranslocation (Tg C/yr)':20.6,'  fixation (Tg C/yr)':0.8,
       'C cost of P acquisition (Pg C/yr)':1.6,'  as % of NPP (P)':5.0,'  direct root P (Tg C/yr)':859.6,'  mycorrhizal P (Tg C/yr)':781.6,'  retranslocation P (Tg C/yr)':4.2,
       'GPP (Pg C/yr)':None,'NPP (Pg C/yr)':32.2,'CUE = NPP/GPP (%)':20.,'TOTVEGC (Pg C)':None,'TOTSOMC (Pg C)':None}
def load(lab):
    d=nc.Dataset(D+f'{lab}_{period}_h0mean.nc'); w=np.nan_to_num(d['area'][:]*1e6*d['landfrac'][:])
    def G(v,scale=1.,flux=True):
        if v not in d.variables: return np.nan
        x=np.ma.filled(d[v][:].astype(float),np.nan); x=np.where(np.isfinite(x)&(np.abs(x)<1e30),x,0.)
        return float((x*w).sum())*(spy if flux else 1.)*scale
    r={}
    r['N uptake total (Tg N/yr)']=G('NUPTAKE',1e-12) if 'NUPTAKE' in d.variables else (G('NACTIVE',1e-12)+G('NNONMYC',1e-12)+G('NRETRANS',1e-12)+G('NFIX',1e-12))
    r['  mycorrhizal (Tg N/yr)']=G('NACTIVE',1e-12); r['    AM (Tg N/yr)']=G('NAM',1e-12); r['    EcM (Tg N/yr)']=G('NECM',1e-12)
    r['  direct root (Tg N/yr)']=G('NNONMYC',1e-12); r['  retranslocation (Tg N/yr)']=G('NRETRANS',1e-12); r['  symbiotic fixation (Tg N/yr)']=G('NFIX',1e-12)
    r['total BNF symbiotic+free-living (Tg N/yr)']=G('NFIX',1e-12)+G('FFIX_TO_SMINN',1e-12)
    r['P uptake total (Tg P/yr)']=G('PUPTAKE',1e-12) if 'PUPTAKE' in d.variables else (G('PACTIVE',1e-12)+G('PNONMYC',1e-12)+G('PRETRANS',1e-12))
    r['  mycorrhizal (Tg P/yr)']=G('PACTIVE',1e-12); r['    AM (Tg P/yr)']=G('PAM',1e-12); r['    EcM (Tg P/yr)']=G('PECM',1e-12); r['  direct root (Tg P/yr)']=G('PNONMYC',1e-12); r['  retranslocation (Tg P/yr)']=G('PRETRANS',1e-12)
    npp=G('NPP',1e-15); gpp=G('GPP',1e-15)
    r['C cost of N acquisition (Pg C/yr)']=G('NPP_NUPTAKE',1e-15); r['  as % of NPP']=100*r['C cost of N acquisition (Pg C/yr)']/npp
    r['  mycorrhizal (Tg C/yr)']=G('NPP_NACTIVE',1e-12); r['  direct root (Tg C/yr)']=G('NPP_NNONMYC',1e-12); r['  retranslocation (Tg C/yr)']=G('NPP_NRETRANS',1e-12); r['  fixation (Tg C/yr)']=G('NPP_NFIX',1e-12)
    r['C cost of P acquisition (Pg C/yr)']=G('NPP_PUPTAKE',1e-15); r['  as % of NPP (P)']=100*r['C cost of P acquisition (Pg C/yr)']/npp
    r['  direct root P (Tg C/yr)']=G('NPP_PNONMYC',1e-12); r['  mycorrhizal P (Tg C/yr)']=G('NPP_PACTIVE',1e-12); r['  retranslocation P (Tg C/yr)']=G('NPP_PRETRANS',1e-12)
    r['GPP (Pg C/yr)']=gpp; r['NPP (Pg C/yr)']=npp; r['CUE = NPP/GPP (%)']=100*npp/gpp; r['TOTVEGC (Pg C)']=G('TOTVEGC',1e-15,False); r['TOTSOMC (Pg C)']=G('TOTSOMC',1e-15,False)
    r['realized symbiotic fixation cost (gC/gN)']=(G('NPP_NFIX')/G('NFIX')) if G('NFIX')>0 else np.nan
    r['NPP before N+P cost (Pg C/yr)']=npp+r['C cost of N acquisition (Pg C/yr)']+r['C cost of P acquisition (Pg C/yr)']
    return r
res={lab:load(lab) for lab in labels}
keys=list(paper.keys())+['realized symbiotic fixation cost (gC/gN)','NPP before N+P cost (Pg C/yr)']
hdr='| quantity | paper (1994–2005) | '+' | '.join(labels)+' |'; lines=[f'# Headline numbers, {period} means\n',hdr,'|---|---|'+'---|'*len(labels)]
def f(x): return '' if x is None or (isinstance(x,float) and np.isnan(x)) else (f'{x:,.1f}' if abs(x)>=10 else f'{x:.2f}')
for k in keys: lines.append(f'| {k} | {f(paper.get(k))} | '+' | '.join(f(res[l][k]) for l in labels)+' |')
if len(labels)>=2:
    a,b=labels[0],labels[1]; lines.append(f'\nΔ({b} − {a}) in %: '+'; '.join(f'{k.strip()}: {100*(res[b][k]-res[a][k])/res[a][k]:+.1f}' for k in ['NPP (Pg C/yr)','GPP (Pg C/yr)','C cost of N acquisition (Pg C/yr)','  mycorrhizal (Tg C/yr)','  direct root (Tg C/yr)','  symbiotic fixation (Tg N/yr)','TOTVEGC (Pg C)'] if res[a][k]))
open(f'numbers_{period}.md','w').write('\n'.join(lines)+'\n'); json.dump(res,open(f'numbers_{period}.json','w'),indent=1)
print('\n'.join(lines))
