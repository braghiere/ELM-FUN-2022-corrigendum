#!/usr/bin/env python3
"""Carbon-budget closure test for one 2-year case (corrigendum, 2026-09-20).
 usage: analyze_cbal.py <casename>
 (1) global budget from the daily h1 stream: integral of (GPP - ER - fire - harvest/product - land-use - leaching - truncation) vs the change
     of TOTCOLC (+TOTPRODC) between the first and last day; FUN cost terms listed separately;
 (2) per-cell residual map statistics (which cells/PFTs carry the gap);
 (3) the CBALREF lines from lnd.log (Amazon reference column, every step): size of the internal column balance error, and
 (4) the number and size of 'column cbalance error' reports."""
import sys, glob, re, numpy as np, netCDF4 as nc, os
case=sys.argv[1]; R=f'/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/runs/{case}/run/'
h1=sorted(glob.glob(R+f'{case}.clm2.h1.*.nc')); print(f'== {case}: {len(h1)} daily-stream files'); 
def cat(v):
    out=[]
    for f in h1:
        d=nc.Dataset(f); 
        if v not in d.variables: return None
        x=np.ma.filled(d[v][:].astype(float),np.nan); out.append(np.where(np.abs(x)<1e30,x,np.nan))
    return np.concatenate(out,axis=0)
d0=nc.Dataset(h1[0]); A=np.nan_to_num(np.ma.filled(d0['area'][:].astype(float),0)*1e6*np.ma.filled(d0['landfrac'][:].astype(float),0)); lat=d0['lat'][:]; lon=d0['lon'][:]
T=cat('GPP').shape[0]; dt=86400.; print(f'   days: {T}')
G=lambda v: (lambda x: None if x is None else np.nansum(np.nan_to_num(x)*A,axis=(1,2)))(cat(v))   # global g C/s per day
flux={v:G(v) for v in ('GPP','NPP','AR','MR','GR','HR','ER','NEE','NEP','NBP','COL_FIRE_CLOSS','PFT_FIRE_CLOSS','WOOD_HARVESTC','PRODUCT_CLOSS','DWT_CLOSS','LAND_USE_FLUX','SOM_C_LEACHED','COL_CTRUNC','PFT_CTRUNC','NPP_NUPTAKE','NPP_PUPTAKE','SOILC_CHANGE')}
stock={v:G(v) for v in ('TOTCOLC','TOTECOSYSC','TOTPRODC','TOTSOMC','TOTVEGC','TOTLITC','CWDC','CPOOL','XSMRPOOL')}
I=lambda v: np.nan if flux.get(v) is None else float(np.nansum(flux[v][1:-1])*dt*1e-15)+0.5*float((flux[v][0]+flux[v][-1])*dt*1e-15)   # Pg C over the span (trapezoid on daily means)
span=(T-1)/365.
print(f'   span {span:.2f} yr. Integrated fluxes (Pg C over the span; per year in brackets):')
for v in flux:
    if flux[v] is not None: print(f'      {v:16s} {I(v):9.3f}  ({I(v)/span:7.3f}/yr)')
dS=lambda v: np.nan if stock.get(v) is None else float((stock[v][-1]-stock[v][0])*1e-15)
print('   stock changes first->last day (Pg C):', {v:round(dS(v),3) for v in stock if stock[v] is not None})
fire=I('COL_FIRE_CLOSS') if flux['COL_FIRE_CLOSS'] is not None else I('PFT_FIRE_CLOSS')
out=I('ER')+fire+I('WOOD_HARVESTC')+I('PRODUCT_CLOSS')-I('SOM_C_LEACHED') if flux['WOOD_HARVESTC'] is not None else I('ER')+fire+I('PRODUCT_CLOSS')-I('SOM_C_LEACHED')
dcol=dS('TOTCOLC')+ (dS('TOTPRODC') if not np.isnan(dS('TOTPRODC')) else 0.)
print(f'   BALANCE (model-flux definition, as EcosystemBalanceCheckMod): GPP {I("GPP"):.3f} - [ER {I("ER"):.3f} + fire {fire:.3f} + harvest {I("WOOD_HARVESTC"):.3f} + product loss {I("PRODUCT_CLOSS"):.3f} - leached {I("SOM_C_LEACHED"):.3f}] = {I("GPP")-out:.3f} Pg C')
print(f'           vs dTOTCOLC {dS("TOTCOLC"):.3f} (+ dTOTPRODC {dS("TOTPRODC"):.3f}) = {dcol:.3f} Pg C  ->  RESIDUAL {I("GPP")-out-dcol:+.3f} Pg C over {span:.2f} yr = {(I("GPP")-out-dcol)/span:+.3f} Pg C/yr')
print(f'   for reference: NBP integral {I("NBP"):.3f}, NEE {I("NEE"):.3f}, NEP {I("NEP"):.3f}, DWT_CLOSS {I("DWT_CLOSS"):.3f}, LAND_USE_FLUX {I("LAND_USE_FLUX"):.3f}, truncation COL {I("COL_CTRUNC"):.4f} PFT {I("PFT_CTRUNC"):.4f}, FUN cost N {I("NPP_NUPTAKE"):.3f} P {I("NPP_PUPTAKE"):.3f}, AR-MR-GR {I("AR")-I("MR")-I("GR"):.3f}')
# per-cell residual
def cell(v): x=cat(v); return None if x is None else np.nansum(np.nan_to_num(x)[1:-1],axis=0)*dt+0.5*(np.nan_to_num(x)[0]+np.nan_to_num(x)[-1])*dt
gpp=cell('GPP'); er=cell('ER'); fi=cell('COL_FIRE_CLOSS') if flux['COL_FIRE_CLOSS'] is not None else cell('PFT_FIRE_CLOSS'); pl=cell('PRODUCT_CLOSS'); le=cell('SOM_C_LEACHED'); hv=cell('WOOD_HARVESTC') if flux['WOOD_HARVESTC'] is not None else 0*gpp
tc=cat('TOTCOLC'); dtc=np.nan_to_num(tc[-1])-np.nan_to_num(tc[0]); res=gpp-(er+fi+pl+hv-le)-dtc   # g C/m2 over span
land=A>0; w=A[land]; r=res[land]
print(f'   per-cell residual (g C/m2 over the span): area-weighted mean {np.sum(r*w)/w.sum():+.2f}, median {np.median(r):+.2f}, 5-95 % {np.percentile(r,5):+.1f} / {np.percentile(r,95):+.1f}; cells with |res| > 10: {np.sum(np.abs(r)>10)} of {land.sum()}; sum {np.sum(r*w)*1e-15:+.3f} Pg C')
pct=np.ma.filled(d0['PCT_NAT_PFT'][:].astype(float),0) if 'PCT_NAT_PFT' in d0.variables else None
if pct is not None:
    dom=np.argmax(np.where(np.abs(pct)<1e30,pct,0),axis=0)
    for p in range(17):
        m=land&(dom==p)
        if m.sum(): print(f'      dominant PFT {p:2d}: {m.sum():4d} cells, residual sum {np.sum(res[m]*A[m])*1e-15:+.3f} Pg C, mean {np.sum(res[m]*A[m])/A[m].sum():+.2f} g C/m2')
# CBALREF lines and error reports from the land log
logs=sorted(glob.glob(R+'lnd.log.*'),key=os.path.getmtime); txt=''
for L in logs: txt+=open(L,errors='ignore').read()
ref=np.array([[float(x) for x in l.split()[2:9]] for l in txt.splitlines() if l.startswith('CBALREF')]) if 'CBALREF' in txt else np.zeros((0,7))
print(f'   CBALREF steps: {len(ref)}')
if len(ref):
    inn,outt,er_,ar_,fire_,dC,err=ref.T
    print(f'      sums over the run (g C/m2): in {inn.sum():.1f}, out {outt.sum():.1f}, er {er_.sum():.1f}, ar {ar_.sum():.1f}, fire {fire_.sum():.2f}, dC {dC.sum():.1f}, err sum {err.sum():+.4f}, max|err| {np.abs(err).max():.2e}, steps |err|>1e-4: {np.sum(np.abs(err)>1e-4)}')
nerr=len(re.findall(r'column cbalance error',txt)); vals=[float(x) for x in re.findall(r'errcb\s*=\s*([-+0-9.Ee]+)',txt)]
print(f'   "column cbalance error" reports: {nerr}; largest |errcb| reported: {max(map(abs,vals)) if vals else 0:.3e}')
