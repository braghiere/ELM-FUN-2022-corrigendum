#!/usr/bin/env python3
"""Global carbon-budget closure: GPP - AR - HR - fire - land-use flux vs d(TOTECOSYSC)/dt, per product/period.
Tests the double counting of FUN acquisition carbon (booked into AR in the 2022 tree and respired again as HR after entering the soil)."""
import netCDF4 as nc, numpy as np, glob, sys
spy=86400*365.; P='/home/braghiere/ELM_FUN_output/'; RR='/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/runs/'
def one_file(f,y0,y1,label):
    d=nc.Dataset(f); t=d['time'][:]; yrs=1850+np.floor((t-15)/365.).astype(int); idx=np.where((yrs>=y0)&(yrs<=y1))[0]; a,b=idx[0],idx[-1]+1
    A=np.nan_to_num(d['area'][:]*1e6*d['landfrac'][:]); V=set(d.variables)
    def G(v):
        if v not in V: return np.nan
        x=np.ma.filled(d[v][a:b].astype(float),0.); x=np.where(np.abs(x)<1e30,x,0.); return float((x.mean(axis=0)*A).sum())*spy/1e15
    def S(v,i): x=np.ma.filled(d[v][i].astype(float),0.); x=np.where(np.abs(x)<1e30,x,0.); return float((x*A).sum())/1e15
    rep(label,y0,y1,G,(S('TOTECOSYSC',b-1)-S('TOTECOSYSC',a))/((b-a)/12.))
def many_files(fs,y0,y1,label):
    fs=[f for f in fs if y0<=int(f.rsplit('.',2)[1][:4])<=y1]; d0=nc.Dataset(fs[0]); A=np.nan_to_num(d0['area'][:]*1e6*d0['landfrac'][:]); V=set(d0.variables)
    acc={}; 
    for f in fs:
        d=nc.Dataset(f)
        for v in ('GPP','AR','HR','NEE','NBP','COL_FIRE_CLOSS','DWT_CONV_CFLUX_GRC','LAND_USE_FLUX','PRODUCT_CLOSS','NPP_NUPTAKE','NPP_PUPTAKE','WOOD_HARVESTC'):
            if v in V: x=np.ma.filled(d[v][0].astype(float),0.); acc[v]=acc.get(v,0.)+float((np.where(np.abs(x)<1e30,x,0.)*A).sum())
    def G(v): return acc[v]/len(fs)*spy/1e15 if v in acc else np.nan
    def S(f): x=np.ma.filled(nc.Dataset(f)['TOTECOSYSC'][0].astype(float),0.); return float((np.where(np.abs(x)<1e30,x,0.)*A).sum())/1e15
    rep(label,y0,y1,G,(S(fs[-1])-S(fs[0]))/(len(fs)/12.))
def rep(label,y0,y1,G,dC):
    gpp,ar,hr=G('GPP'),G('AR'),G('HR'); fire=np.nan_to_num(G('COL_FIRE_CLOSS')); luc=G('DWT_CONV_CFLUX_GRC'); luc=np.nan_to_num(luc if np.isfinite(luc) else G('LAND_USE_FLUX')); prod=np.nan_to_num(G('PRODUCT_CLOSS')); cost=np.nan_to_num(G('NPP_NUPTAKE'))+np.nan_to_num(G('NPP_PUPTAKE'))
    resid=gpp-ar-hr-fire-luc-prod
    print(f"-- {label} {y0}-{y1}: GPP {gpp:6.1f} AR {ar:5.1f} HR {hr:5.1f} fire {fire:4.1f} LUC {luc:4.1f} prod {prod:4.1f} | NEE(diag) {G('NEE'):6.1f} NBP(diag) {G('NBP'):6.1f} | GPP-AR-HR-fire-LUC-prod = {resid:6.1f} vs dC/dt {dC:6.2f} -> unexplained {resid-dC:6.1f} | FUN cost N+P {cost:5.1f} Pg C/yr",flush=True)
one_file(P+'ELM/ELM.clm2.h0.185001-201012.nc',1994,2005,'published ELM (FUN off)')
one_file(P+'ELM_FUN/ELM_FUN.clm2.h0.185001-201012.nc',1994,2005,'published FUN2 (N only)')
one_file(P+'ELM_FUNP/ELM_FUNP.clm2.h0.185001-201012.nc',1994,2005,'published FUNP')
one_file(P+'ELM_FUNP/ELM_FUNP.clm2.h0.185001-201012.nc',1860,1879,'published FUNP')
many_files(sorted(glob.glob(RR+'corr22ctl_f19_f19_ICB20TRCNPRDCTCBC/run/*.clm2.h0.18??-??.nc')),1860,1879,'control rerun (FUN-P on, 2022 tree)')
fs=sorted(glob.glob(RR+'corr22spin20_f19_f19_ICB1850CNPRDCTCBC/run/*.clm2.h0.*.nc'))
d0=nc.Dataset(fs[-1]); A=np.nan_to_num(d0['area'][:]*1e6*d0['landfrac'][:]); 
def G(v): x=np.ma.filled(d0[v][0].astype(float),0.); return float((np.where(np.abs(x)<1e30,x,0.)*A).sum())*spy/1e15
print(f"-- FN spin-up (FUN off, 2020 tree), last 20-yr mean: GPP {G('GPP'):6.1f} AR {G('AR'):5.1f} HR {G('HR'):5.1f} fire {G('COL_FIRE_CLOSS'):4.1f} | GPP-AR-HR-fire = {G('GPP')-G('AR')-G('HR')-G('COL_FIRE_CLOSS'):6.1f} (equilibrium -> ~0 expected)")
