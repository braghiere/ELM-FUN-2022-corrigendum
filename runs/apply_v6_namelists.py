#!/usr/bin/env python3
"""Make each case's user_nl_clm v6-identical by templating from the surviving v6 files.
Substitutions only: run-dir paths, or-hydra inputdata -> overlay, case names in finidat, and an
explicit hist_fincl1 for FN/TR so pathway fluxes + pools are in h0. Usage:
  apply_v6_namelists.py <caseroot_prefix e.g. .../cime/scripts/corr22ctl> <runroot> <phase: ad|fn|tr> <casename> [ad_casename] [fn_casename]
Writes <case>/user_nl_clm (backs up OLMT's as user_nl_clm.olmt)."""
import sys, re, shutil, os
prefix, runroot, phase, case = sys.argv[1:5]; ad = sys.argv[5] if len(sys.argv)>5 else ''; fn = sys.argv[6] if len(sys.argv)>6 else ''
B='/home/braghiere/ELM-FUN-2022-corrigendum/runs/v6_baseline_namelists/'
v6={'ad':'fix_global_v6_funp_f19_f19_ICB1850CNRDCTCBC_ad_spinup','fn':'fix_global_v6_funp_f19_f19_ICB1850CNPRDCTCBC','tr':'fix_global_v6_funp_f19_f19_ICB20TRCNPRDCTCBC'}[phase]
t=open(B+v6+'.user_nl_clm').read()
OV='/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/inputdata'
t=t.replace('/lustre/or-hydra/cades-ccsi/proj-shared/project_acme/ACME_inputdata',OV)
t=re.sub(r"/lustre/or-hydra/cades-ccsi/scratch/braghiere/[^/']+/run/", runroot+'/'+case+'/run/', t)
if phase=='fn': t=t.replace('fix_global_v6_funp_f19_f19_ICB1850CNRDCTCBC_ad_spinup.clm2.r.0261', ad+'.clm2.r.0261')
if phase=='tr': t=t.replace('fix_global_v2_f19_f19_ICB1850CNPRDCTCBC.clm2.r.0541', fn+'.clm2.r.0281')   # this OLMT restarts FN clock at 1: 280 yr -> r.0281
# make sure pathway C fluxes + pools land in h0 for FN and TR (v6's h0 already carried NPP_NACTIVE etc. as defaults)
F1=("'NPP_NACTIVE','NPP_NNONMYC','NPP_NFIX','NPP_NRETRANS','NPP_NAM','NPP_NECM','NPP_PACTIVE','NPP_PNONMYC','NPP_PRETRANS','NPP_PAM','NPP_PECM',"
    "'NPP_NUPTAKE','NPP_PUPTAKE','NACTIVE','NNONMYC','NFIX','NRETRANS','NAM','NECM','PACTIVE','PNONMYC','PAM','PECM',"
    "'COST_NACTIVE','COST_NFIX','COST_NNONMYC','COST_NRETRANS','COST_PACTIVE','COST_PNONMYC','COST_PRETRANS',"
    "'NUPTAKE_NPP_FRACTION','PUPTAKE_NPP_FRACTION','AVAILC','GPP','NPP','AR','HR','NEE','TOTVEGC','TOTVEGN','TOTVEGP','TOTSOMC','TOTSOMN','TOTSOMP',"
    "'TOTECOSYSC','TOTLITC','SMINN','SMINP','SOLUTIONP','TLAI','PCT_NAT_PFT'")
if phase in ('fn','tr') and 'hist_fincl1' not in t:
    t=t.replace('&clm_inparm\n','&clm_inparm\n hist_fincl1 = '+F1+'\n',1)
dst=f'{prefix}/{case}/user_nl_clm'
if os.path.exists(dst) and not os.path.exists(dst+'.olmt'): shutil.copy(dst,dst+'.olmt')
open(dst,'w').write(t); print('wrote',dst)
