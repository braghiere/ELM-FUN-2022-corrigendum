#!/usr/bin/env python3
"""Template each case's user_nl_clm from the namelists that actually produced the published product:
  ad, fn : the v2 spin-up cases (FUN off, use_lch4 on, co2 constant) -> runs/v2_spinup_namelists/   [shared by both chains]
  tr     : the v6 FUN-P transient                                    -> runs/v6_baseline_namelists/
Substitutions only: or-hydra inputdata -> overlay; run-dir paths -> our run dirs; finidat case names
(AD r.0261 -> FN; FN r.0541 -> TR, the restart year the published transient branched from); paramfile ->
/home/braghiere/clm_params_c200626.nc (identical to the 2020 clm_params_c180524.nc in all 294 shared
parameters; it only adds the FUN entries the 2022 code reads unconditionally). TR gets an explicit
hist_fincl1 with the pathway fluxes/pools.
Usage: apply_namelists.py <caseroot_prefix_dir> <runroot> <ad|fn|tr> <casename> [ad_casename] [fn_casename]"""
import sys, re, shutil, os
prefix, runroot, phase, case = sys.argv[1:5]; ad = sys.argv[5] if len(sys.argv)>5 else ''; fn = sys.argv[6] if len(sys.argv)>6 else ''
R='/home/braghiere/ELM-FUN-2022-corrigendum/runs/'
src={'ad':R+'v2_spinup_namelists/fix_global_v2_f19_f19_ICB1850CNRDCTCBC_ad_spinup.user_nl_clm',
     'fn':R+'v2_spinup_namelists/fix_global_v2_f19_f19_ICB1850CNPRDCTCBC.user_nl_clm',
     'tr':R+'v6_baseline_namelists/fix_global_v6_funp_f19_f19_ICB20TRCNPRDCTCBC.user_nl_clm'}[phase]
t=open(src).read()
OV='/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/inputdata'
t=t.replace('/lustre/or-hydra/cades-ccsi/proj-shared/project_acme/ACME_inputdata',OV)
# paramfile: v2 used an OLMT-staged copy of clm_params_c180524.nc (gone with or-hydra); c200626 is identical in every shared parameter
PF=os.environ.get('PARAMFILE','/home/braghiere/clm_params_c200626.nc')   # spin-up in the 2020 tree: set PARAMFILE to the c180524 copy (identical shared values)
t=re.sub(r"paramfile *= *'[^']*'", "paramfile = '"+PF+"'", t)
if phase=='fn':
    t=t.replace('fix_global_v2_f19_f19_ICB1850CNRDCTCBC_ad_spinup.clm2.r.0261', ad+'.clm2.r.0261')
    t=re.sub(r"finidat *= *'[^']*/run/", "finidat = '"+runroot+'/'+ad+'/run/', t)
if phase=='tr':
    # the v6 file fco2_datm_1765-2007 ends in 2007 and the model reads past it (PCO2 -> 0 by mid-2010 in the archived products);
    # use the RCP4.5 series (identical 1850-2005, covers 2006-2010) — the same file the 2020 spin-up used
    t=t.replace('fco2_datm_1765-2007_c100614.nc','fco2_datm_rcp4.5_1765-2500_c130312.nc')
    t=t.replace('fix_global_v2_f19_f19_ICB1850CNPRDCTCBC.clm2.r.0541', fn+'.clm2.r.0541')   # fn = corr22spin20_f19_f19_ICB1850CNPRDCTCBC (shared spin-up)
    t=re.sub(r"finidat *= *'[^']*/run/", "finidat = '"+runroot+'/'+fn+'/run/', t)
t=re.sub(r"/lustre/or-hydra/cades-ccsi/scratch/braghiere/[^/']+/run/", runroot+'/'+case+'/run/', t)
F1=("'NPP_NACTIVE','NPP_NNONMYC','NPP_NFIX','NPP_NRETRANS','NPP_NAM','NPP_NECM','NPP_PACTIVE','NPP_PNONMYC','NPP_PRETRANS','NPP_PAM','NPP_PECM',"
    "'NPP_NUPTAKE','NPP_PUPTAKE','NACTIVE','NNONMYC','NFIX','NRETRANS','NAM','NECM','PACTIVE','PNONMYC','PAM','PECM',"
    "'COST_NACTIVE','COST_NFIX','COST_NNONMYC','COST_NRETRANS','COST_PACTIVE','COST_PNONMYC','COST_PRETRANS',"
    "'NUPTAKE_NPP_FRACTION','PUPTAKE_NPP_FRACTION','AVAILC','GPP','NPP','AR','HR','NEE','TOTVEGC','TOTVEGN','TOTVEGP','TOTSOMC','TOTSOMN','TOTSOMP',"
    "'TOTECOSYSC','TOTLITC','SMINN','SMINP','SOLUTIONP','TLAI','PCT_NAT_PFT'")
if phase=='tr' and 'hist_fincl1' not in t:
    t=t.replace('&clm_inparm\n','&clm_inparm\n hist_fincl1 = '+F1+'\n',1)
assert "or-hydra" not in t, "unsubstituted or-hydra path left in namelist"
dst=f'{prefix}/{case}/user_nl_clm'
if os.path.exists(dst) and not os.path.exists(dst+'.olmt'): shutil.copy(dst,dst+'.olmt')
if os.path.exists(dst): shutil.copy(dst, dst+'.prev')
open(dst,'w').write(t); print('wrote',dst,'from',os.path.basename(src))
