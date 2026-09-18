#!/usr/bin/env python3
"""Aggregate NTSG MOD17A3 annual NPP (30 arcsec GeoTIFF, uint16, scale 1e-4 kg C m-2 yr-1, fill >= 65500) 2000-2015 to 0.5 deg,
then to the f19 grid; write zonal mean (g C m-2 yr-1) and 0.5-deg map. Block-wise to limit memory."""
import glob, numpy as np, rasterio, netCDF4 as nc
B='/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/benchmarks/modis_mod17a3/'; fs=sorted(glob.glob(B+'MOD17A3_Science_NPP_*.tif'))
S=np.zeros((360,720)); N=np.zeros((360,720)); fac=60   # 30 arcsec -> 0.5 deg = 60 px
for f in fs:
    with rasterio.open(f) as ds:
        H,W=ds.height,ds.width; b=ds.bounds; assert W==43200 and H%60==0,(H,W); top=b.top; r_off=int(round((90-top)*120))//60   # 0.5-deg row offset of the raster's top edge
        for r0 in range(0,H,1800):
            a=ds.read(1,window=((r0,r0+1800),(0,W))).astype('f8'); good=(a<65500)&(a>=0); a=np.where(good,a*1e-4*1000.,0.)   # g C m-2 yr-1
            rb=r0//fac+r_off; nb=a.shape[0]//fac; S[rb:rb+nb]+=a.reshape(nb,fac,720,fac).sum(axis=(1,3)); N[rb:rb+nb]+=good.reshape(nb,fac,720,fac).sum(axis=(1,3))
    print('  ',f.split('_')[-1][:4],'done; raster bounds',ds.bounds)
npp05=np.where(N>0,S/np.maximum(N,1),np.nan); frac=N/(len(fs)*fac*fac)   # mean over years and valid pixels; frac = valid coverage
lat05=90-0.25-np.arange(360)*0.5; lon05=-180+0.25+np.arange(720)*0.5
o=nc.Dataset('/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/benchmarks/modis_mod17a3_npp_2000-2015_0.5deg.nc','w'); o.createDimension('lat',360); o.createDimension('lon',720)
for k,x in (('lat',lat05),('lon',lon05)): v=o.createVariable(k,'f8',(k,)); v[:]=x
v=o.createVariable('npp','f4',('lat','lon'),fill_value=np.float32(1e36)); v[:]=np.where(np.isfinite(npp05),npp05,1e36); v.units='g C m-2 yr-1'; v.long_name='MOD17A3 (NTSG) mean annual NPP 2000-2015, valid-pixel mean'
v=o.createVariable('valid_frac','f4',('lat','lon')); v[:]=frac; o.close()
# zonal mean over valid (vegetated) 0.5-deg cells, weighted by cos(lat) and valid coverage
w=np.cos(np.deg2rad(lat05))[:,None]*frac; zon=np.nansum(np.nan_to_num(npp05)*w,axis=1)/np.where(w.sum(axis=1)>0,w.sum(axis=1),np.nan)
np.savez('/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/data/benchmarks/modis_npp_zonal.npz',lat=lat05,npp=zon)
print('   wrote modis_mod17a3_npp_2000-2015_0.5deg.nc and modis_npp_zonal.npz; global vegetated-mean NPP = %.0f g C m-2 yr-1'%np.nanmean(npp05))
