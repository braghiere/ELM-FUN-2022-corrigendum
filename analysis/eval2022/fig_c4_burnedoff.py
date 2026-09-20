#!/usr/bin/env python3
"""Diagnostic figure for the C4-grass dominance of the FUN carbon cost and the burned-off carbon term (control run, 1994-2005 means).
(a) map: nutrient-acquisition carbon as % of pre-cost NPP, C4-dominated cells outlined; (b) realized N price vs soil mineral N per cell;
(c,d) N and P cost by dominant vegetation group split into pathway cost and burned-off carbon."""
import numpy as np, netCDF4 as nc, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
SURF,T1,T2,GRID='#fcfcfb','#0b0b0b','#52514e','#e6e4df'; BLUE,ORANGE,AQUA,GRAY='#2a78d6','#eb6834','#1baf7a','#b5b3ad'
SEQ=['#cde2fb','#b7d3f6','#9ec5f4','#86b6ef','#6da7ec','#5598e7','#3987e5','#2a78d6','#256abf','#1c5cab','#184f95','#104281','#0d366b']
spy=86400*365.
def fld(d,v): x=np.ma.filled(d[v][:].astype(float),np.nan); return np.where(np.abs(x)<1e30,x,np.nan)
d=nc.Dataset('data/control_1994-2005_h0mean.nc'); lat=d['lat'][:]; lon=d['lon'][:]; A=np.nan_to_num(fld(d,'area')*1e6*fld(d,'landfrac')); pct=np.nan_to_num(fld(d,'PCT_NAT_PFT')); dom=np.argmax(pct,axis=0)
npp=fld(d,'NPP'); nc_=fld(d,'NPP_NUPTAKE'); pc_=fld(d,'NPP_PUPTAKE'); pre=npp+nc_+pc_; frac=100*(nc_+pc_)/np.where(pre>1e-9,pre,np.nan); frac=np.where((A>0)&(dom>0),frac,np.nan)
nup=sum(fld(d,v) for v in ('NACTIVE','NNONMYC','NRETRANS','NFIX')); price=nc_/np.where(nup>1e-12,nup,np.nan)*1.0; sminn=fld(d,'SMINN')
B=json.load(open('burnedoff_by_group.json'))['control']
plt.rcParams.update({'font.size':9,'text.color':T1,'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'axes.edgecolor':GRID,'figure.facecolor':SURF,'axes.facecolor':SURF,'savefig.facecolor':SURF})
fig=plt.figure(figsize=(13,8.6)); gs=fig.add_gridspec(2,2,height_ratios=[1.15,1],hspace=0.38,wspace=0.28)
# (a) map
ax=fig.add_subplot(gs[0,0]); bounds=[0,5,10,15,20,30,40,50,60,80]; cmap=ListedColormap(SEQ[1:1+len(bounds)-1]); norm=BoundaryNorm(bounds,cmap.N)
lon2=np.where(lon>180,lon-360,lon); o=np.argsort(lon2); pm=ax.pcolormesh(lon2[o],lat,frac[:,o],cmap=cmap,norm=norm,shading='nearest',rasterized=True)
c4=((dom==14)&(pct[14]>50)&(A>0)).astype(float); ax.contour(lon2[o],lat,c4[:,o],levels=[0.5],colors=T1,linewidths=0.7)
cb=fig.colorbar(pm,ax=ax,orientation='horizontal',fraction=0.05,pad=0.08,ticks=bounds); cb.outline.set_visible(False); cb.set_label('carbon spent on N and P acquisition, % of pre-cost NPP (NPP + NPP_NUPTAKE + NPP_PUPTAKE)',color=T2)
ax.set_xlim(-180,180); ax.set_ylim(-60,85); ax.set_xticks([]); ax.set_yticks([]); [s.set_visible(False) for s in ax.spines.values()]
ax.set_title('a  Where the nutrient cost bites (control run, 1994–2005)\n    outline: cells with > 50 % C4 grass',loc='left',fontsize=10,color=T1)
# (b) scatter
ax=fig.add_subplot(gs[0,1]); ok=(A>0)&(dom>0)&np.isfinite(price)&np.isfinite(sminn)&(sminn>0)&(price>0)
groups=[('other vegetated',~np.isin(dom,[4,13,14]),GRAY),('tropical broadleaf evergreen trees',dom==4,BLUE),('C3 grass',dom==13,AQUA),('C4 grass',dom==14,ORANGE)]
for name,m,col in groups:
    mm=ok&m; ax.scatter(sminn[mm],price[mm],s=22,c=col,edgecolors=SURF,linewidths=0.6,label=f'{name} dominant ({mm.sum()} cells)' if name!='other vegetated' else f'{name} ({mm.sum()} cells)',zorder=3 if col!=GRAY else 2)
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('soil mineral N, g N m$^{-2}$ (SMINN, 1994–2005 mean)'); ax.set_ylabel('realized N price, g C per g N acquired')
ax.grid(True,color=GRID,lw=0.6); [s.set_visible(False) for s in ax.spines.values()]; ax.legend(frameon=False,fontsize=8,loc='upper right')
ax.set_title('b  The carbon price of nitrogen falls with soil mineral N\n    C4-grass cells sit in the nitrogen-poor corner',loc='left',fontsize=10,color=T1)
# (c,d) bars
order=sorted([g for g in B if g!='bare/other'],key=lambda g: B[g]['Ncost']+B[g]['Pcost'],reverse=True)
for k,(nut,tot,burn,title) in enumerate((('N','Ncost','Nburn','c  Carbon cost of N acquisition by dominant vegetation group'),('P','Pcost','Pburn','d  Carbon cost of P acquisition by dominant vegetation group'))):
    ax=fig.add_subplot(gs[1,k]); y=np.arange(len(order))[::-1]
    path=np.array([B[g][tot]-B[g][burn] for g in order]); bo=np.array([B[g][burn] for g in order])
    ax.barh(y,path,height=0.62,color=BLUE,edgecolor=SURF,linewidth=1.5,label='paid to a pathway (mycorrhizal, root, retranslocation, fixation)')
    ax.barh(y,bo,left=path,height=0.62,color=ORANGE,edgecolor=SURF,linewidth=1.5,label='burned-off carbon (spent, no nutrient obtained)')
    for yi,g in zip(y,order): t=B[g][tot]; ax.text(t+0.03,yi,f'{t:.2f}'+(f'  ({100*B[g][burn]/t:.0f} % burned)' if B[g][burn]/max(t,1e-9)>0.05 else ''),va='center',fontsize=8,color=T2)
    ax.set_yticks(y); ax.set_yticklabels(order); ax.set_xlabel(f'Pg C yr$^{{-1}}$  (global {nut} cost {sum(B[g][tot] for g in B):.2f}, burned-off {sum(B[g][burn] for g in B):.2f})'); ax.set_xlim(0,max(path+bo)*1.55)
    ax.grid(True,axis='x',color=GRID,lw=0.6); ax.set_axisbelow(True); [s.set_visible(False) for s in ax.spines.values()]; ax.tick_params(length=0)
    ax.set_title(title,loc='left',fontsize=10,color=T1)
    if k==0: ax.legend(frameon=False,fontsize=8,loc='center right',bbox_to_anchor=(1.0,0.45))
fig.text(0.01,0.005,'ELM-FUN3.0 control rerun (released 2020 code), 1994–2005 means; cells grouped by the dominant natural PFT; bare/other cells omitted from c and d (N 0.02, P 0.24 Pg C/yr).',fontsize=7.5,color=T2)
out='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/fig_c4grass_burnedoff_control_1994-2005.png'; plt.savefig(out,dpi=130,bbox_inches='tight'); print('wrote',out)
