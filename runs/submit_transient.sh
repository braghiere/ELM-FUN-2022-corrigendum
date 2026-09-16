#!/bin/bash
# One FUN-P transient (1850-2010, 161 yr) branching from the shared FN restart r.0541. Usage: submit_transient.sh <prefix> <FN_jobid>
set -e; P=$1; J_FN=$2; R=/home/braghiere/ELM-FUN-2022-corrigendum; W=$R/runs/wrappers; LOG=$R/runs/submit_${P}.log
$R/runs/make_wrappers.sh $P >/dev/null
J_TR=$(sbatch --parsable -d afterok:$J_FN $W/${P}_TR.sbatch); echo "  TR($P) -> $J_TR (afterok FN $J_FN)  $(date)" | tee -a $LOG
echo "$P TR=$J_TR (afterok FN $J_FN) $(date +%F)" >> $R/runs/jobids.txt
