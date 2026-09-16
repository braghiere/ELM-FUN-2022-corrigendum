#!/bin/bash
# Submit one chain AD -> FN -> TR with SLURM afterok dependencies, one long job per phase (batch has no time limit),
# email on END/FAIL of each phase. Usage: submit_chain.sh <prefix> [walltime e.g. 3-00:00:00]
set -e
P=$1; WALL=${2:-3-00:00:00}; MAIL=renatob@caltech.edu
CR=/home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts
AD=${P}_f19_f19_ICB1850CNRDCTCBC_ad_spinup; FN=${P}_f19_f19_ICB1850CNPRDCTCBC; TR=${P}_f19_f19_ICB20TRCNPRDCTCBC
LOG=/home/braghiere/ELM-FUN-2022-corrigendum/runs/submit_${P}.log
sub(){ # $1=case $2=dependency-jobid-or-empty
  cd $CR/$1
  ./xmlchange JOB_WALLCLOCK_TIME=$WALL,RESUBMIT=0,CONTINUE_RUN=FALSE
  ./xmlchange --subgroup case.run BATCH_COMMAND_FLAGS="--mail-user=$MAIL --mail-type=END,FAIL" 2>/dev/null || true
  local dep=""; [ -n "$2" ] && dep="--prereq $2"
  local out; out=$(./case.submit $dep 2>&1); echo "$out" >> $LOG
  echo "$out" | grep -o "Submitted job id [0-9]*\|Submitted batch job [0-9]*" | grep -o "[0-9]*$" | head -1
}
echo "=== submit chain $P  $(date)" | tee -a $LOG
J_AD=$(sub $AD "");      echo "  AD $AD -> job $J_AD"  | tee -a $LOG
J_FN=$(sub $FN "$J_AD"); echo "  FN $FN -> job $J_FN (afterok $J_AD)" | tee -a $LOG
J_TR=$(sub $TR "$J_FN"); echo "  TR $TR -> job $J_TR (afterok $J_FN)" | tee -a $LOG
echo "$P AD=$J_AD FN=$J_FN TR=$J_TR" >> /home/braghiere/ELM-FUN-2022-corrigendum/runs/jobids.txt
