#!/usr/bin/env python3
"""Re-plot Ashley's ELM-FUN comparison from replot_data.json. Panel A: what she plotted (COST sums, efficiencies).
Panel B: the comparable carbon flux NPP_NACTIVE+NPP_PACTIVE, labelled with the share of pre-cost NPP
(NPP+NPP_NUPTAKE+NPP_PUPTAKE), because the 2022 build books the FUN cost into autotrophic respiration."""
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=json.load(open('/home/braghiere/ashley_mycorrhizal/replot_data.json')); A=d['ashley_x_from_figure']; E=d['elm_groups']
groups=list(A.keys()); cols=plt.cm.YlGnBu(np.linspace(0.3,0.95,len(groups)))
fig,ax=plt.subplots(1,2,figsize=(17.5,7.4))
fig.suptitle('Re-plot of the ELM-FUN comparison with the correct variable  (ELM: fix_global_v6_funp, 1994–2005 mean, dominant-PFT >30%, NPP>100 gC m$^{-2}$ yr$^{-1}$; bars = p10–p90; PROVISIONAL, corrected rerun in progress)',fontsize=11)
for g,c in zip(groups,cols):
    x,lo,hi=A[g]; e=E[g]
    ax[0].errorbar(x,e['cost_sum'],xerr=[[x-lo],[hi-x]],fmt='D',ms=9,color=c,mec='k',ecolor=c,capsize=3,label=g)
    ax[1].errorbar(x,e['mycC'],xerr=[[x-lo],[hi-x]],yerr=[[e['mycC']-e['p10']],[e['p90']-e['mycC']]],fmt='D',ms=9,color=c,mec='k',ecolor=c,capsize=3,label=g)
    off={'EcM Needle-leaf Trees and Shrubs':(-78,-14),'ECM Evergreen Needle Trees':(7,9),'EcM Broadleaf Trees and Shrubs':(7,-14)}.get(g,(7,5))
    ax[1].annotate(f"{e['pct_gross']:.1f}% of NPP",(x,e['mycC']),xytext=off,textcoords='offset points',fontsize=8.5)
ax[0].plot([0,20],[0,20],'--',color='gray',lw=1); ax[0].set_xlim(0,120); ax[0].set_ylim(0,20)
ax[0].set_title('A. As plotted: COST_NACTIVE + COST_PACTIVE\n(these are gN/gC + gP/gC efficiencies, NOT a carbon flux)',fontsize=11)
ax[0].set_xlabel('Hyphal C allocation, this study  (gC m$^{-2}$ yr$^{-1}$)  [group means read from figure]'); ax[0].set_ylabel('ELM "cost" sum  (gN/gC + gP/gC)')
ax[0].text(0.42,0.85,'1:1 line is meaningless here:\nunits differ on the two axes',transform=ax[0].transAxes,color='firebrick',fontsize=10)
ax[1].plot([3,300],[3,300],'--',color='gray',lw=1,label='1:1'); ax[1].set_xscale('log'); ax[1].set_yscale('log'); ax[1].set_xlim(3,300); ax[1].set_ylim(1,300)
ax[1].set_title('B. Corrected: NPP_NACTIVE + NPP_PACTIVE\n(carbon actually spent on mycorrhizal N+P uptake; % = share of NPP before the N+P acquisition cost)',fontsize=11)
ax[1].set_xlabel('Hyphal C allocation, this study  (gC m$^{-2}$ yr$^{-1}$)  [group means read from figure]'); ax[1].set_ylabel('ELM mycorrhizal C allocation  (gC m$^{-2}$ yr$^{-1}$)')
ax[1].legend(fontsize=8.5,loc='upper left'); [a.grid(alpha=.3) for a in ax]
plt.tight_layout(rect=(0,0,1,0.95)); plt.savefig('/home/braghiere/ashley_mycorrhizal/replot_hyphal_vs_ELM_corrected.png',dpi=130); print('   figure written')
