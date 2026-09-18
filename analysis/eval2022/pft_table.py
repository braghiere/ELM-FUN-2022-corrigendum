#!/usr/bin/env python3
"""Per-PFT breakdown (area, NPP, C cost of N and P acquisition, N uptake) from *_pftmean.nc, side by side. Usage: pft_table.py <period> <labels...>"""
import sys, numpy as np, netCDF4 as nc
period=sys.argv[1]; labels=sys.argv[2:]; D='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/'; spy=86400*365.
names=['bare','NET temperate','NET boreal','NDT boreal','BET tropical','BET temperate','BDT tropical','BDT temperate','BDT boreal','BES','BDS temperate','BDS boreal','C3 arctic grass','C3 grass','C4 grass','C3 crop','C3 irrigated']
rows=[]; hdr='| PFT | area (Mkm2) | '+' | '.join(f'{l}: N cost Tg C/yr (g C m-2 yr-1) / P cost Tg C/yr / NPP Pg C/yr' for l in labels)+' |'
out=[f'# Per-PFT breakdown, {period}\n',hdr,'|---|---|'+'---|'*len(labels)]
for p in range(17):
    cells=[]
    for l in labels:
        pf=nc.Dataset(D+f'{l}_{period}_pftmean.nc'); h0=nc.Dataset(D+f'{l}_{period}_h0mean.nc'); A=np.nan_to_num(h0['area'][:]*1e6*h0['landfrac'][:]); wt=np.array(pf['pft_wtgcell'][:])
        g=lambda v: np.where(np.abs(pf[v][p])<1e30,pf[v][p],0); W=(wt[p]*A).sum()
        cells.append(f"{(g('NPP_NUPTAKE')*A).sum()*spy/1e12:7.1f} ({(g('NPP_NUPTAKE')*A).sum()*spy/max(W,1):6.1f}) / {(g('NPP_PUPTAKE')*A).sum()*spy/1e12:7.1f} / {(g('NPP')*A).sum()*spy/1e15:5.2f}")
    out.append(f'| {p} {names[p]} | {W/1e12:6.2f} | '+' | '.join(cells)+' |')
open(f'pft_table_{period}.md','w').write('\n'.join(out)+'\n'); print('\n'.join(out))
