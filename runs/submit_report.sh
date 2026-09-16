#!/bin/bash
# Final analysis after both transients. Usage: submit_report.sh <TR_ctl_jobid> <TR_abc_jobid>
R=/home/braghiere/ELM-FUN-2022-corrigendum; RR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/runs
J=$(sbatch --parsable -d afterok:$1:$2 --output=$R/runs/logs/report.%j.out $R/runs/final_report.sbatch \
   "control:$RR/corr22ctl_f19_f19_ICB20TRCNPRDCTCBC/run/corr22ctl_f19_f19_ICB20TRCNPRDCTCBC.clm2.h0.*.nc" \
   "corrected_ABC:$RR/corr22abc_f19_f19_ICB20TRCNPRDCTCBC/run/corr22abc_f19_f19_ICB20TRCNPRDCTCBC.clm2.h0.*.nc")
echo "  REPORT -> $J (afterok $1 $2)"; echo "REPORT=$J (afterok $1 $2) $(date +%F)" >> $R/runs/jobids.txt
