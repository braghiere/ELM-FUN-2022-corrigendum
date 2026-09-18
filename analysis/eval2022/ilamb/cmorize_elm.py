#!/usr/bin/env python3
"""CMORize monthly ELM h0 output for ILAMB, matching the 2022 files in ELM_FUN_output/ELM_output (one variable per file,
<var>_Lmon_<model>_r1i1p1_185001-201012.nc, kg m-2 s-1 etc.). Usage: cmorize_elm.py <model_name> <h0_glob> <outdir> [y0 y1]
Only the variables used by the 2022 ILAMB configuration are produced."""
import sys, glob, numpy as np, netCDF4 as nc, warnings, datetime; warnings.filterwarnings('ignore')
model,h0p,out=sys.argv[1:4]; y0=int(sys.argv[4]) if len(sys.argv)>4 else 1850; y1=int(sys.argv[5]) if len(sys.argv)>5 else 2010
fs=[f for f in sorted(glob.glob(h0p)) if y0<=int(f.rsplit('.',2)[1][:4])<=y1]; assert fs, h0p
G2KG=1e-3
CMOR={ # name: (elm vars, factor, units, long_name)
 'gpp':(['GPP'],G2KG,'kg m-2 s-1','Carbon Mass Flux out of Atmosphere due to Gross Primary Production on Land'),
 'npp':(['NPP'],G2KG,'kg m-2 s-1','Net Primary Production on Land'),'nbp':(['NBP'],G2KG,'kg m-2 s-1','Net Biome Production'),
 'ra':(['AR'],G2KG,'kg m-2 s-1','Autotrophic Respiration'),'rh':(['HR'],G2KG,'kg m-2 s-1','Heterotrophic Respiration'),
 'nee':(['NEE'],G2KG,'kg m-2 s-1','Net Ecosystem Exchange'),'lai':(['TLAI'],1.,'1','Leaf Area Index'),
 'cVeg':(['TOTVEGC'],G2KG,'kg m-2','Carbon Mass in Vegetation'),'cSoil':(['TOTSOMC'],G2KG,'kg m-2','Carbon Mass in Soil Pool'),
 'hfls':(['EFLX_LH_TOT'],1.,'W m-2','Surface Upward Latent Heat Flux'),'hfss':(['FSH'],1.,'W m-2','Surface Upward Sensible Heat Flux'),
 'tas':(['TSA'],1.,'K','Near-Surface Air Temperature'),'pr':(['RAIN','SNOW'],1.,'kg m-2 s-1','Precipitation'),
 'rsds':(['FSDS'],1.,'W m-2','Surface Downwelling Shortwave Radiation'),'evspsbl':(['QSOIL','QVEGE','QVEGT'],1.,'kg m-2 s-1','Evaporation')}
d0=nc.Dataset(fs[0]); lat=d0['lat'][:]; lon=d0['lon'][:]; avail={k:v for k,v in CMOR.items() if all(x in d0.variables for x in v[0])}
print(f'   {model}: {len(fs)} months, {len(avail)} variables: {sorted(avail)}')
data={k:np.zeros((len(fs),len(lat),len(lon)),'f4') for k in avail}; time=np.zeros(len(fs)); tb=np.zeros((len(fs),2))
mdays=[31,28,31,30,31,30,31,31,30,31,30,31]
for i,f in enumerate(fs):
    d=nc.Dataset(f); y=int(f.rsplit('.',2)[1][:4]); m=int(f.rsplit('.',2)[1][5:7]); t0=(y-1850)*365+sum(mdays[:m-1]); tb[i]=[t0,t0+mdays[m-1]]; time[i]=t0+mdays[m-1]/2.
    for k,(vs,fac,_,_) in avail.items():
        x=sum(np.ma.filled(d[v][0].astype(float),np.nan) for v in vs); x=np.where(np.isfinite(x)&(np.abs(x)<1e30),x*fac,np.nan); data[k][i]=x
tag=f'{y0}01-{y1}12'
for k,(vs,fac,units,ln) in avail.items():
    o=nc.Dataset(f'{out}/{k}_Lmon_{model}_r1i1p1_{tag}.nc','w'); o.createDimension('time',None); o.createDimension('lat',len(lat)); o.createDimension('lon',len(lon)); o.createDimension('nb',2)
    t=o.createVariable('time','f8',('time',)); t[:]=time; t.units='days since 1850-01-01 00:00:00'; t.calendar='noleap'; t.bounds='time_bounds'
    b=o.createVariable('time_bounds','f8',('time','nb')); b[:]=tb
    la=o.createVariable('lat','f8',('lat',)); la[:]=lat; la.units='degrees_north'; lo=o.createVariable('lon','f8',('lon',)); lo[:]=lon; lo.units='degrees_east'
    v=o.createVariable(k,'f4',('time','lat','lon'),fill_value=np.float32(-1e20)); v[:]=np.where(np.isfinite(data[k]),data[k],-1e20); v.units=units; v.long_name=ln; v.cell_methods='time: mean'
    o.source=f'ELM h0 {model}; cmorize_elm.py {datetime.date.today()}'; o.close()
print('   done ->',out)
