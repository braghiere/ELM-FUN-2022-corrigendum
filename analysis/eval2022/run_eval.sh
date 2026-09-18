#!/bin/bash
# Master driver: redo the Braghiere et al. (2022) evaluation side by side (published product vs control rerun vs corrected rerun).
# Run after both transients have finished (h0/h1 monthly files 1850-2010 present). Usage: ./run_eval.sh [period, default 1994-2005]
set -u; cd /home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022
PER=${1:-1994-2005}; Y0=${PER%-*}; Y1=${PER#*-}; PY=/home/braghiere/miniconda3/bin/python
PUB=/home/braghiere/ELM_FUN_output; RR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/runs
CTL=$RR/corr22ctl_f19_f19_ICB20TRCNPRDCTCBC/run; ABC=$RR/corr22abc_f19_f19_ICB20TRCNPRDCTCBC/run
LOG=run_eval_$PER.log; echo "=== run_eval $PER $(date)" | tee $LOG
step(){ echo "--- $1" | tee -a $LOG; shift; "$@" 2>&1 | tee -a $LOG; }
# 1. period means (h0 gridded + h1 per-PFT)
[ -f data/published_FUNP_${PER}_pftmean.nc ] || step "prep published_FUNP" $PY prep_means.py published_FUNP $PUB/ELM_FUNP/ELM_FUNP.clm2.h0.185001-201012.nc $PUB/fix_global_v6_funp_h1.nc $Y0 $Y1
[ -f data/published_ELM_${PER}_h0mean.nc ]   || step "prep published_ELM"  $PY prep_means.py published_ELM  $PUB/ELM/ELM.clm2.h0.185001-201012.nc none $Y0 $Y1
[ -f data/published_FUN2_${PER}_h0mean.nc ]  || step "prep published_FUN2" $PY prep_means.py published_FUN2 $PUB/ELM_FUN/ELM_FUN.clm2.h0.185001-201012.nc none $Y0 $Y1
step "prep control"   $PY prep_means.py control   "$CTL/*.clm2.h0.????-??.nc" "$CTL/*.clm2.h1.????-??.nc" $Y0 $Y1
step "prep corrected" $PY prep_means.py corrected "$ABC/*.clm2.h0.????-??.nc" "$ABC/*.clm2.h1.????-??.nc" $Y0 $Y1
# 2. annual series 1850-2010 (published products once; reruns always)
for lab in published_FUNP:$PUB/ELM_FUNP/ELM_FUNP.clm2.h0.185001-201012.nc published_FUN2:$PUB/ELM_FUN/ELM_FUN.clm2.h0.185001-201012.nc published_ELM:$PUB/ELM/ELM.clm2.h0.185001-201012.nc; do
  l=${lab%%:*}; f=${lab#*:}; [ -f data/${l}_series.npz ] || step "series $l" $PY npp_series.py $l "$f"; done
step "series control"   $PY npp_series.py control   "$CTL/*.clm2.h0.????-??.nc"
step "series corrected" $PY npp_series.py corrected "$ABC/*.clm2.h0.????-??.nc"
# 3. numbers and figures
step "headline numbers" $PY headline_numbers.py $PER published_FUNP control corrected
step "per-PFT table"    $PY pft_table.py $PER published_FUNP control corrected
for f in 5 6 7 S5; do step "fig $f" $PY fig_maps.py $PER $f published_FUNP control corrected; done
step "fig 8"  $PY fig8_biomes.py $PER published_FUNP control corrected
step "fig 9"  $PY fig9_limitation.py $PER published_FUNP published_FUNP control corrected
step "fig 3/4/S10/S11" $PY fig3_4.py published_ELM published_FUN2 published_FUNP control corrected
# 4. ILAMB: CMORize the reruns (full 1850-2010; their CO2 forcing is valid to 2010) and benchmark all five products
IR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/ilamb_root
mkdir -p $IR/MODELS/control $IR/MODELS/corrected
step "cmorize control"   $PY ilamb/cmorize_elm.py control   "$CTL/*.clm2.h0.????-??.nc" $IR/MODELS/control
step "cmorize corrected" $PY ilamb/cmorize_elm.py corrected "$ABC/*.clm2.h0.????-??.nc" $IR/MODELS/corrected
step "ILAMB all five" bash -c "cd $IR && ILAMB_ROOT=$IR /home/braghiere/miniconda3/envs/ilamb/bin/ilamb-run --config /home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/ilamb/ilamb_elmfun.cfg --model_root $IR/MODELS --models ELM ELM_FUN ELM_FUNP control corrected --study_limits $Y0 $Y1 --regions global --build_dir $IR/_build_all_$PER"
cp $IR/_build_all_$PER/scores.csv ilamb/scores_all_$PER.csv 2>/dev/null
echo "=== done $(date)" | tee -a $LOG
