#!/usr/bin/env python3
"""Figure 1 for Ashley: carbon spent on mycorrhizal fungi, ELM-FUN (2022 run, 1994-2005) vs her study, by her vegetation groups.
Paired horizontal bars; reference categorical palette slots 1-2 (validated adjacent pair); text in ink tokens."""
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=json.load(open('replot_data.json')); A=d['ashley_x_from_figure']; E=d['elm_groups']
groups=list(A.keys())
labels={'AM Crops':'AM crops','AM Natural Grasses':'AM natural grasses','AM Trees and Shrubs':'AM trees and shrubs',
        'EcM Broadleaf Trees and Shrubs':'EcM broadleaf trees and shrubs','EcM Needle-leaf Trees and Shrubs':'EcM needleleaf trees and shrubs',
        'ECM Deciduous Needle Trees':'EcM deciduous needleleaf trees','ECM Evergreen Needle Trees':'EcM evergreen needleleaf trees'}
elm=[E[g]['mycC'] for g in groups]; her=[A[g][0] for g in groups]; pct=[E[g]['pct_gross'] for g in groups]
BLUE,ORANGE='#2a78d6','#eb6834'; INK,INK2,SURF,GRID='#0b0b0b','#52514e','#fcfcfb','#e6e5e1'
fig,ax=plt.subplots(figsize=(10.5,6.2)); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
y=np.arange(len(groups))[::-1]; h=0.36
b1=ax.barh(y+h/2+0.02,elm,height=h,color=BLUE,label='ELM-FUN model (2022 run, 1994 to 2005 average)')
b2=ax.barh(y-h/2-0.02,her,height=h,color=ORANGE,label='This study (hyphal C allocation, group means)')
for yi,v,p in zip(y+h/2+0.02,elm,pct): ax.text(v+1.5,yi,f"{v:.0f}   ({p:.1f}% of NPP)",va='center',ha='left',fontsize=9,color=INK2)
for yi,v in zip(y-h/2-0.02,her): ax.text(v+1.5,yi,f"{v:.0f}",va='center',ha='left',fontsize=9,color=INK2)
ax.set_yticks(y); ax.set_yticklabels([labels[g] for g in groups],fontsize=10.5,color=INK)
ax.set_xlabel('Carbon sent to mycorrhizal fungi  (grams of carbon per square metre per year)',fontsize=10.5,color=INK)
ax.set_xlim(0,135); ax.xaxis.grid(True,color=GRID,lw=0.8); ax.set_axisbelow(True)
for s in ('top','right','left'): ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(GRID); ax.tick_params(axis='x',colors=INK2,labelsize=9.5); ax.tick_params(axis='y',length=0)
ax.set_title('How much carbon do plants pay their mycorrhizal fungi?',loc='left',fontsize=13.5,color=INK,pad=38)
ax.text(0,1.03,'ELM-FUN percentages are the share of NPP (before the nutrient cost is paid).\nStudy values are group means read from your figures, about ±3 g C m⁻² yr⁻¹.',
        transform=ax.transAxes,fontsize=9.3,color=INK2,va='bottom')
ax.legend(loc='lower right',frameon=False,fontsize=9.5,labelcolor=INK)
plt.tight_layout(); plt.savefig('fig1_ELM_vs_thisstudy_by_group.png',dpi=150,facecolor=SURF); print('   wrote fig1_ELM_vs_thisstudy_by_group.png')
