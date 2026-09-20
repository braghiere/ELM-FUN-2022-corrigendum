#!/usr/bin/env python3
"""Why do C4 grasses pay ~10x more carbon per unit N than other PFTs? Monthly climatology (1994-2005, archived product) for grid cells
dominated (>50 %) by C4 grass, C3 grass, tropical broadleaf evergreen trees: N cost, N uptake, cost per N, mineral N (total and by layer),
fine-root C, leaf C, LAI, N demand, and the soil-N vertical profile."""
import netCDF4 as nc, numpy as np, json
d=nc.Dataset('/home/braghiere/ELM_FUN_output/ELM_FUNP/ELM_FUNP.clm2.h0.185001-201012.nc'); A=np.nan_to_num(d['area'][:]*1e6*d['landfrac'][:]); spy=86400*365.
m=nc.Dataset('/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/published_FUNP_1994-2005_h0mean.nc'); pct=np.nan_to_num(np.where(np.abs(m['PCT_NAT_PFT'][:])<1e30,m['PCT_NAT_PFT'][:],0)); dom=np.argmax(pct,axis=0)
a,b=(1994-1850)*12,(2006-1850)*12
V=[v for v in ('NPP_NUPTAKE','NACTIVE','NNONMYC','NRETRANS','NFIX','SMINN','SMIN_NO3','SMIN_NH4','FROOTC','LEAFC','TLAI','PLANT_NDEMAND','NPP','GPP','COST_NACTIVE','COST_NNONMYC','FPG','FPI','NET_NMIN','GROSS_NMIN','SMINN_TO_PLANT','QDRAI','RAIN','TSA','BTRAN','NDEP_TO_SMINN','SMIN_NO3_LEACHED','F_DENIT','SMIN_NO3_vr','SMIN_NH4_vr','ROOTFR','SOILN_vr') if v in d.variables]
print("   variables used:",V)
groups={'C4 grass':14,'C3 grass':13,'BET tropical':4,'BDT tropical':6,'C3 crop':15}
masks={g:(dom==p)&(pct[p]>50)&(A>0) for g,p in groups.items()}
out={}
for g,mk in masks.items():
    w=A[mk]; out[g]={'n_cells':int(mk.sum())}
    for v in V:
        x=np.ma.filled(d[v][a:b].astype(float),np.nan); x=np.where(np.abs(x)<1e30,x,np.nan)
        if x.ndim==4:   # vertically resolved (time, lev, lat, lon): area-weighted profile mean
            prof=np.array([np.nansum(np.nan_to_num(x[:,k])[:,mk]*w,axis=1).mean()/w.sum() for k in range(x.shape[1])]); out[g][v+'_profile']=prof.tolist(); continue
        ts=np.nansum(np.nan_to_num(x)[:,mk]*w,axis=1)/w.sum()   # monthly area-weighted mean
        clim=ts.reshape(12,12).mean(axis=0)
        out[g][v]={'mean':float(ts.mean()),'clim':clim.tolist()}
    c=out[g]; unit=lambda v,f=spy: c[v]['mean']*f if v in c else np.nan
    nup=unit('NACTIVE')+unit('NNONMYC')+unit('NRETRANS')+unit('NFIX')
    print(f"-- {g:13s} n={mk.sum():4d} | N cost {unit('NPP_NUPTAKE'):6.1f} gC/m2/yr | N uptake {nup:5.1f} gN/m2/yr -> {unit('NPP_NUPTAKE')/nup:5.2f} gC/gN | N demand {unit('PLANT_NDEMAND'):5.1f} | SMINN {unit('SMINN',1):5.2f} (NO3 {unit('SMIN_NO3',1):5.2f} NH4 {unit('SMIN_NH4',1):5.2f}) gN/m2 | FROOTC {unit('FROOTC',1):5.0f} LEAFC {unit('LEAFC',1):5.0f} gC/m2 | LAI {unit('TLAI',1):4.2f} | NPP {unit('NPP'):5.0f} | net Nmin {unit('NET_NMIN'):5.1f} gN/m2/yr | FPG {unit('FPG',1):4.2f} | COST_NACTIVE {unit('COST_NACTIVE',1):5.2f} gN/gC")
    if 'SMIN_NO3_vr_profile' in c: print("      NO3 profile (gN/m3, top 8 layers):",np.round(c['SMIN_NO3_vr_profile'][:8],3).tolist()); 
    if 'SMIN_NH4_vr_profile' in c: print("      NH4 profile (gN/m3, top 8 layers):",np.round(c['SMIN_NH4_vr_profile'][:8],3).tolist())
    if 'ROOTFR_profile' in c: print("      root fraction profile (top 8):",np.round(c['ROOTFR_profile'][:8],3).tolist())
    print("      seasonal N cost (gC/m2/yr by month):",np.round(np.array(c['NPP_NUPTAKE']['clim'])*spy,0).astype(int).tolist(),"| SMINN by month:",np.round(c['SMINN']['clim'],2).tolist() if 'SMINN' in c else '')
json.dump(out,open('c4grass_diag.json','w'))
