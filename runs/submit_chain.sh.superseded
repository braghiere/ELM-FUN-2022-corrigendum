#!/bin/bash
# Submit one chain: AD -> adjust_restart -> FN -> TR, SLURM afterok, OLMT-style wrappers. Usage: submit_chain.sh <prefix>
set -e; P=$1; R=/home/braghiere/ELM-FUN-2022-corrigendum; W=$R/runs/wrappers; RR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/runs
MAIL=renatob@caltech.edu; LOG=$R/runs/submit_${P}.log
$R/runs/make_wrappers.sh $P >/dev/null
AD=${P}_f19_f19_ICB1850CNRDCTCBC_ad_spinup
echo "=== submit chain $P $(date)" | tee -a $LOG
J_AD=$(sbatch --parsable $W/${P}_AD.sbatch);                                   echo "  AD  -> $J_AD" | tee -a $LOG
J_ADJ=$(sbatch --parsable -d afterok:$J_AD --mail-user=$MAIL --mail-type=FAIL --output=$R/runs/logs/${P}_ADJ.%j.out $R/runs/adjust_restart.sbatch $AD $RR); echo "  ADJ -> $J_ADJ (afterok $J_AD)" | tee -a $LOG
J_FN=$(sbatch --parsable -d afterok:$J_ADJ $W/${P}_FN.sbatch);                 echo "  FN  -> $J_FN (afterok $J_ADJ)" | tee -a $LOG
J_TR=$(sbatch --parsable -d afterok:$J_FN $W/${P}_TR.sbatch);                  echo "  TR  -> $J_TR (afterok $J_FN)" | tee -a $LOG
echo "$P AD=$J_AD ADJ=$J_ADJ FN=$J_FN TR=$J_TR $(date +%F)" >> $R/runs/jobids.txt
