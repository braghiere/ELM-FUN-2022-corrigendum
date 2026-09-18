#!/usr/bin/env python3
"""Annual global series (1850-2010) and 1994-2005 zonal means for Figures 3a, 4a, S10, S11a.
Usage: npp_series.py <label> <h0_glob_or_file>   -> data/<label>_series.npz (years, GPP, NPP, AR, HR, NBP in Pg C/yr; zonal NPP 1994-2005 g C m-2 yr-1)"""
import sys, glob, numpy as np, netCDF4 as nc, warnings; warnings.filterwarnings('ignore')
label,h0p=sys.argv[1:3]; D='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/'; spy=86400*365.; V=['GPP','NPP','AR','HR','NBP']
fs=sorted(glob.glob(h0p)); d=nc.Dataset(fs[0]); area=np.nan_to_num(d['area'][:]*1e6*d['landfrac'][:]); lat=d['lat'][:]; lf=np.nan_to_num(d['landfrac'][:]); A=np.nan_to_num(d['area'][:]*1e6)
def g(x): x=np.ma.filled(x.astype(float),0.); x=np.where(np.abs(x)<1e30,x,0.); return float((x*area).sum())*spy/1e15
years={}; zon=np.zeros(len(lat)); zn=0; zonw=(A*lf).sum(axis=1)
mdays=np.array([31,28,31,30,31,30,31,31,30,31,30,31])/365.
if len(fs)==1:
    t=d['time'][:]; yrs=1850+np.floor((t-15.)/365.).astype(int)
    for y in np.unique(yrs):
        idx=np.where(yrs==y)[0]; years[int(y)]={v:float(sum(g(d[v][i])*mdays[k%12] for k,i in enumerate(idx))) for v in V if v in d.variables}
        if 1994<=y<=2005:
            for k,i in enumerate(idx): x=np.ma.filled(d['NPP'][i].astype(float),0.); x=np.where(np.abs(x)<1e30,x,0.); zon+=(x*A*lf).sum(axis=1)/np.where(zonw>0,zonw,np.nan)*spy*mdays[k]; zn+=1
else:
    for f in fs:
        y=int(f.rsplit('.',2)[1][:4]); m=int(f.rsplit('.',2)[1][5:7]); dd=nc.Dataset(f)
        years.setdefault(y,{v:0. for v in V if v in dd.variables})
        for v in years[y]: years[y][v]+=g(dd[v][0])*mdays[m-1]
        if 1994<=y<=2005: x=np.ma.filled(dd['NPP'][0].astype(float),0.); x=np.where(np.abs(x)<1e30,x,0.); zon+=(x*A*lf).sum(axis=1)/np.where(zonw>0,zonw,np.nan)*spy*mdays[m-1]; zn+=1
yy=sorted(years); full=[y for y in yy if all(k in years[y] for k in years[yy[0]])]
np.savez(D+f'{label}_series.npz',years=np.array(full),**{v:np.array([years[y].get(v,np.nan) for y in full]) for v in V},zonal_npp_1994_2005=(zon/(zn/12) if zn else zon*np.nan),lat=lat,months_in_zonal=zn)
print(f'   {label}: {len(full)} years ({full[0]}-{full[-1]}); NPP first/last {years[full[0]].get("NPP",np.nan):.1f}/{years[full[-1]].get("NPP",np.nan):.1f} Pg C/yr; zonal months {zn}')
