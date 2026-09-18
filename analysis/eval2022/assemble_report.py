#!/usr/bin/env python3
"""Assemble EVAL2022_REPORT.md from the driver outputs (numbers table, per-PFT table, ILAMB scores, Fig 9 classes, figure list).
Usage: assemble_report.py <period>"""
import sys, os, json, glob
per=sys.argv[1] if len(sys.argv)>1 else '1994-2005'; D='/home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/'
def rd(p): return open(p).read() if os.path.exists(p) else f'_(missing: {os.path.basename(p)})_\n'
out=[f"# Braghiere et al. (2022) evaluation redone side by side — {per} means\n",
     "Columns: **published_FUNP** = archived ELM-FUN3.0 (v6, Zenodo 10.5281/zenodo.20452251); **control** = same code, fresh spin-up, "
     "2020 surface dataset, CO₂ covering 2006–2010; **corrected** = control + bundled fixes A (larch kc/kn), B (PFT-7 tier, inert), C (fixation cost).\n",
     "## Headline numbers (paper Table/Results)\n", rd(D+f'numbers_{per}.md').split('\n',2)[-1],
     "\n## Per-PFT breakdown\n", rd(D+f'pft_table_{per}.md').split('\n',2)[-1],
     "\n## Nutrient-limitation classes (Fig. 9)\n"]
for f in sorted(glob.glob(D+f'fig9_thresholds_{per}.json')): out.append('```\n'+rd(f)+'```\n')
out.append("\n## ILAMB overall scores (all five products)\n"); sc=D+f'ilamb/scores_all_{per}.csv'
if os.path.exists(sc):
    rows=[l.split(',') for l in open(sc).read().strip().split('\n')]; out.append('| '+' | '.join(rows[0])+' |\n|'+'---|'*len(rows[0])+'\n')
    for r in rows[1:]: out.append('| '+' | '.join(x if not x.replace('.','',1).isdigit() else f'{float(x):.2f}' for x in r)+' |\n')
else: out.append(rd(sc))
out.append("\n## Figures\n"); 
for f in sorted(glob.glob(D+f'fig*_{per}_*.png'))+sorted(glob.glob(D+'fig3_4_S10_S11_*.png')): out.append(f"- [{os.path.basename(f)}]({os.path.basename(f)})\n")
out.append("\n## Findings independent of the reruns\nSee `paper_numbers_provenance.md`, `ilamb/ILAMB_vs_paper_fig2.md`, `budget_closure.log`, `SNEAK_PEEK_1860-1879.md`.\n")
open(D+'EVAL2022_REPORT.md','w').write(''.join(out)); print('   wrote EVAL2022_REPORT.md')
