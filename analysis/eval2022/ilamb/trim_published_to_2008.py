import netCDF4 as nc, sys, glob, os
src,dst,nt=sys.argv[1],sys.argv[2],int(sys.argv[3])
for f in sorted(glob.glob(src+'/*_185001-201012.nc')):
    o=dst+'/'+os.path.basename(f).replace('185001-201012','185001-200812')
    if os.path.exists(o) and os.path.getsize(o)>1e6: continue
    d=nc.Dataset(f); w=nc.Dataset(o,'w',format='NETCDF4_CLASSIC')
    for k,dim in d.dimensions.items(): w.createDimension(k,None if dim.isunlimited() else len(dim))
    for k,v in d.variables.items():
        fv=getattr(v,'_FillValue',None); x=w.createVariable(k,v.dtype,v.dimensions,fill_value=fv); x.setncatts({a:v.getncattr(a) for a in v.ncattrs() if a!='_FillValue'})
        x[:]=v[:nt] if 'time' in v.dimensions else v[:]
    w.setncatts({a:d.getncattr(a) for a in d.ncattrs()}); w.close()
print('   trimmed',os.path.basename(src),len(glob.glob(dst+'/*.nc')),'files')
