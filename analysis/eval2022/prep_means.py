#!/usr/bin/env python3
"""Build period-mean fields for the Braghiere et al. (2022) evaluation, for one run.
  h0  -> gridded means of the FUN pathway fluxes, costs, C budget, states   (lat,lon)
  h1  -> per-PFT gridded means (pft,lat,lon) of the PFT-level stream, scaled by pfts1d_wtgcell (as in the 2020 script)
Usage: prep_means.py <label> <h0_glob_or_file> <h1_glob_or_file> <y0> <y1>
Published product: h0 = /home/braghiere/ELM_FUN_output/ELM_FUNP/ELM_FUNP.clm2.h0.185001-201012.nc, h1 = /home/braghiere/ELM_FUN_output/fix_global_v6_funp_h1.nc
Rerun:             h0 = <run>/*.clm2.h0.????-??.nc, h1 = <run>/*.clm2.h1.????-??.nc
Output: data/<label>_<y0>-<y1>_h0mean.nc and _pftmean.nc (time-mean over all months in [y0,y1]; fluxes kept in model units)."""
import sys, glob, numpy as np, netCDF4 as nc, warnings; warnings.filterwarnings('ignore')
label,h0p,h1p,y0,y1=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5])
OUT='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/'
H0=['GPP','NPP','AR','HR','NEE','NBP','AVAILC','TLAI','TOTVEGC','TOTSOMC','TOTECOSYSC','TOTLITC','TOTVEGN','TOTVEGP','SMINN','SMINP','SOLUTIONP','LEAFC','LEAFN','LEAFP',
    'NPP_NUPTAKE','NPP_PUPTAKE','NPP_NACTIVE','NPP_NNONMYC','NPP_NFIX','NPP_NRETRANS','NPP_NAM','NPP_NECM','NPP_PACTIVE','NPP_PNONMYC','NPP_PRETRANS','NPP_PAM','NPP_PECM',
    'NACTIVE','NNONMYC','NRETRANS','NFIX','NAM','NECM','FFIX_TO_SMINN','NFIX_TO_SMINN','PACTIVE','PNONMYC','PRETRANS','PAM','PECM',
    'COST_NACTIVE','COST_NNONMYC','COST_NRETRANS','COST_NFIX','COST_PACTIVE','COST_PNONMYC','COST_PRETRANS','NUPTAKE_NPP_FRACTION','PUPTAKE_NPP_FRACTION',
    'LEAFN_TO_LITTER','LEAFP_TO_LITTER','LEAFC_TO_LITTER','RETRANSN_TO_NPOOL','RETRANSP_TO_PPOOL','FREE_RETRANSN_TO_NPOOL','FREE_RETRANSP_TO_PPOOL','PCT_NAT_PFT','PCT_LANDUNIT']
H1=['GPP','NPP','AR','HR','NACTIVE','NNONMYC','NFIX','NRETRANS','NAM','NECM','PACTIVE','PNONMYC','PRETRANS','PAM','PECM','NPP_NUPTAKE','NPP_PUPTAKE',
    'COST_NACTIVE','COST_NFIX','COST_NRETRANS','COST_NNONMYC','COST_PACTIVE','COST_PRETRANS','COST_PNONMYC','NUPTAKE_NPP_FRACTION','PUPTAKE_NPP_FRACTION']
def files(p): 
    fs=sorted(glob.glob(p)); return fs
def yr_of(f,d,ti):
    if 'h0.18' in f or 'h0.19' in f or 'h0.20' in f or 'h1.18' in f or 'h1.19' in f or 'h1.20' in f: return int(f.rsplit('.',2)[1][:4])
    t=d['time']; return 1850+int(np.floor(t[ti]/365.))   # single long file: 'days since 1850-01-01' (noleap); mid-month stamps
# ---------- h0 ----------
fs=files(h0p); assert fs, h0p
d=nc.Dataset(fs[0]); lat=d['lat'][:]; lon=d['lon'][:]; area=d['area'][:]; lf=d['landfrac'][:]
vars0=[v for v in H0 if v in d.variables]; acc={v:0. for v in vars0}; n=0
if len(fs)==1:   # one long file
    t=d['time'][:]; yrs=1850+np.floor((t-0.5)/365.).astype(int); idx=np.where((yrs>=y0)&(yrs<=y1))[0]; assert len(idx)==12*(y1-y0+1),(len(idx))
    for v in vars0: acc[v]=np.ma.filled(np.ma.masked_invalid(d[v][idx[0]:idx[-1]+1].astype(float)).mean(axis=0),np.nan)
    n=len(idx)
else:
    for f in fs:
        y=int(f.rsplit('.',2)[1][:4]); 
        if y<y0 or y>y1: continue
        dd=nc.Dataset(f)
        for v in vars0: acc[v]=acc[v]+np.ma.filled(dd[v][0].astype(float),np.nan)
        n+=1
    for v in vars0: acc[v]=acc[v]/n
    assert n==12*(y1-y0+1),(n)
o=nc.Dataset(OUT+f'{label}_{y0}-{y1}_h0mean.nc','w'); o.createDimension('lat',len(lat)); o.createDimension('lon',len(lon)); o.createDimension('natpft',17); o.createDimension('ltype',9)
for k,x in (('lat',lat),('lon',lon)): vv=o.createVariable(k,'f8',(k,)); vv[:]=x
for k,x in (('area',area),('landfrac',lf)): vv=o.createVariable(k,'f8',('lat','lon')); vv[:]=np.ma.filled(x,np.nan)
for v in vars0:
    x=acc[v]; dims=('lat','lon') if x.ndim==2 else (('natpft','lat','lon') if x.shape[0]==17 else ('ltype','lat','lon'))
    vv=o.createVariable(v,'f4',dims,fill_value=np.float32(1e36)); vv[:]=np.where(np.isfinite(x),x,1e36).astype('f4'); vv.units=getattr(d[v],'units',''); vv.long_name=getattr(d[v],'long_name','')
o.months=n; o.period=f'{y0}-{y1}'; o.source=h0p; o.close(); print(f'   {label}: h0 mean over {n} months -> {label}_{y0}-{y1}_h0mean.nc ({len(vars0)} vars)')
# ---------- h1 -> per-PFT grids (skipped if h1 arg is 'none') ----------
if h1p=='none': sys.exit(0)
fs=files(h1p); assert fs, h1p
d=nc.Dataset(fs[0]); it=d['pfts1d_itype_veg'][:].astype(int); ix=d['pfts1d_ixy'][:].astype(int)-1; jy=d['pfts1d_jxy'][:].astype(int)-1; wt=np.ma.filled(d['pfts1d_wtgcell'][:].astype(float),0)
ok=(it>=0)&(it<=16); flat=(it*len(lat)+jy)*len(lon)+ix   # index into (pft,lat,lon)
vars1=[v for v in H1 if v in d.variables and d[v].dimensions[-1]=='pft']
PATH=[('NPPC_NACTIVE','NACTIVE','COST_NACTIVE'),('NPPC_NNONMYC','NNONMYC','COST_NNONMYC'),('NPPC_NRETRANS','NRETRANS','COST_NRETRANS'),('NPPC_NFIX','NFIX','COST_NFIX'),('NPPC_PACTIVE','PACTIVE','COST_PACTIVE'),('NPPC_PNONMYC','PNONMYC','COST_PNONMYC'),('NPPC_PRETRANS','PRETRANS','COST_PRETRANS')]
PATH=[p for p in PATH if p[1] in d.variables and p[2] in d.variables]
acc={v:np.zeros(17*len(lat)*len(lon)) for v in vars1+[p[0] for p in PATH]}; n=0
def add(dd,ti):
    raw={}
    for v in vars1:
        x=np.ma.filled(dd[v][ti].astype(float),0.); x=np.where(np.abs(x)<1e30,x,0.); raw[v]=x; np.add.at(acc[v],flat[ok],(x*wt)[ok])
    for name,nv,cv in PATH:   # pathway C spent this month = nutrient flux / (nutrient per C); COST invalid or 0 -> no C
        c=raw[cv]; nflux=raw[nv]; x=np.where(c>1e-12,nflux/np.where(c>1e-12,c,1.),0.); np.add.at(acc[name],flat[ok],(x*wt)[ok])
if len(fs)==1:
    t=d['time'][:]; yrs=1850+np.floor((t-0.5)/365.).astype(int); idx=np.where((yrs>=y0)&(yrs<=y1))[0]; assert len(idx)==12*(y1-y0+1)
    for ti in idx: add(d,ti); n+=1
else:
    for f in fs:
        y=int(f.rsplit('.',2)[1][:4])
        if y<y0 or y>y1: continue
        add(nc.Dataset(f),0); n+=1
    assert n==12*(y1-y0+1),(n)
wsum=np.zeros(17*len(lat)*len(lon)); np.add.at(wsum,flat[ok],wt[ok])   # PFT weight (fraction of gridcell) per (pft,cell)
o=nc.Dataset(OUT+f'{label}_{y0}-{y1}_pftmean.nc','w'); o.createDimension('pft',17); o.createDimension('lat',len(lat)); o.createDimension('lon',len(lon))
for k,x in (('lat',lat),('lon',lon)): vv=o.createVariable(k,'f8',(k,)); vv[:]=x
vv=o.createVariable('pft_wtgcell','f4',('pft','lat','lon')); vv[:]=wsum.reshape(17,len(lat),len(lon)).astype('f4'); vv.long_name='PFT weight in gridcell (sum of pfts1d_wtgcell); divide gridcell-weighted fluxes by this for per-PFT-area values'
for k,x in (('area',area),('landfrac',lf)): vv=o.createVariable(k,'f8',('lat','lon')); vv[:]=np.ma.filled(x,np.nan)
for v in vars1+[p[0] for p in PATH]:
    vv=o.createVariable(v,'f4',('pft','lat','lon')); vv[:]=(acc[v]/n).reshape(17,len(lat),len(lon)).astype('f4')
    if v in d.variables: vv.units=getattr(d[v],'units',''); vv.long_name=getattr(d[v],'long_name','')+' [gridcell-weighted: value*pfts1d_wtgcell summed per PFT]'
    else: vv.units='gC/m^2/s'; vv.long_name='C spent on this pathway = monthly nutrient flux / COST efficiency, then time-mean [gridcell-weighted]'
o.note='pfts1d_wtgcell is relative to the LAND part of the cell: multiply by area*landfrac for totals'
o.months=n; o.period=f'{y0}-{y1}'; o.source=h1p; o.close(); print(f'   {label}: h1 per-PFT mean over {n} months -> {label}_{y0}-{y1}_pftmean.nc ({len(vars1)} vars)')
