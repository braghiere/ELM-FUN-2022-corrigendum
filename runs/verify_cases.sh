#!/bin/bash
# Post-creation verification for one chain. Usage: verify_cases.sh <prefix e.g. corr22ctl>
P=$1; CR=/home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts; RR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/runs
AD=${P}_f19_f19_ICB1850CNRDCTCBC_ad_spinup; FN=${P}_f19_f19_ICB1850CNPRDCTCBC; TR=${P}_f19_f19_ICB20TRCNPRDCTCBC
PY=/home/braghiere/bin/python
echo "### chain $P"
for c in $AD $FN $TR; do [ -d $CR/$c ] && echo "  case ok: $c" || { echo "  MISSING case: $c"; exit 1; }; done
echo "--- build status"; for c in $AD $FN $TR; do echo "  $c: $(grep -h 'case.build success\|case.build error' $CR/$c/CaseStatus 2>/dev/null | tail -1)"; done
echo "--- apply v6-templated namelists"
$PY $(dirname $0)/apply_v6_namelists.py $CR $RR ad $AD
$PY $(dirname $0)/apply_v6_namelists.py $CR $RR fn $FN $AD
$PY $(dirname $0)/apply_v6_namelists.py $CR $RR tr $TR $AD $FN
echo "--- every .nc path referenced in user_nl_clm must exist (run-dir files excepted: created at run time)"
for c in $AD $FN $TR; do
  grep -o "'[^']*\.nc'" $CR/$c/user_nl_clm | tr -d "'" | sort -u | while read f; do
    case "$f" in *"/run/"*) echo "  [$c] rundir-file (expected later): $(basename $f)";; *) [ -e "$f" ] && echo "  [$c] ok: $(basename $f)" || echo "  [$c] MISSING: $f";; esac
  done
done
echo "--- key env settings"
for c in $AD $FN $TR; do cd $CR/$c; echo "  $c: RUN_STARTDATE=$(./xmlquery --value RUN_STARTDATE) STOP_N=$(./xmlquery --value STOP_N) REST_N=$(./xmlquery --value REST_N) CO2_TYPE=$(./xmlquery --value CLM_CO2_TYPE) CO2_PPMV=$(./xmlquery --value CCSM_CO2_PPMV) NTASKS=$(./xmlquery --value NTASKS_LND) WALL=$(./xmlquery --value JOB_WALLCLOCK_TIME 2>/dev/null)"; done
echo "--- SourceMods in place (md5 must match chain: ctl d0c2fef5…, fix 3eef642f…)"
for c in $AD $FN $TR; do echo "  $c: $(md5sum $CR/$c/SourceMods/src.clm/CNFUNMod.F90 2>/dev/null | cut -c1-8)"; done
echo "--- normalized diff vs v6 baseline (paths/casenames stripped); empty = identical"
B=$(dirname $0)/v6_baseline_namelists
norm(){ sed -e "s|/lustre/[^' ]*/run/|<RUN>/|g; s|/lustre/or-hydra/cades-ccsi/proj-shared/project_acme/ACME_inputdata|<IN>|g; s|/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/inputdata|<IN>|g; s|fix_global_v[26]_[a-z_]*f19_f19|<CASE>|g; s|${P}_f19_f19|<CASE>|g" "$1" | grep -v "hist_fincl1" | grep -v '^\s*$'; }
diff <(norm $B/fix_global_v6_funp_f19_f19_ICB1850CNRDCTCBC_ad_spinup.user_nl_clm) <(norm $CR/$AD/user_nl_clm) && echo "  AD identical"
diff <(norm $B/fix_global_v6_funp_f19_f19_ICB1850CNPRDCTCBC.user_nl_clm)         <(norm $CR/$FN/user_nl_clm) && echo "  FN identical"
diff <(norm $B/fix_global_v6_funp_f19_f19_ICB20TRCNPRDCTCBC.user_nl_clm)          <(norm $CR/$TR/user_nl_clm) && echo "  TR identical"
