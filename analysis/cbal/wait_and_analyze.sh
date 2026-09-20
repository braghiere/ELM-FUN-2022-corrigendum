#!/bin/bash
# waits for a budget-test job, runs the analysis, appends to analysis/cbal/results.log, mails a short note
J=$1; CASE=$2; while squeue -h -j $J 2>/dev/null | grep -q .; do sleep 120; done
OUT=/home/braghiere/ELM-FUN-2022-corrigendum/analysis/cbal/results_${CASE}.log
{ echo "# job $J finished $(date)"; sacct -j $J -o State,Elapsed -n -P | head -1; /home/braghiere/miniconda3/bin/python /home/braghiere/ELM-FUN-2022-corrigendum/analysis/cbal/analyze_cbal.py $CASE; } > $OUT 2>&1
{ echo "Budget test $CASE (job $J) finished. Analysis:"; cat $OUT; } | mail -s "Corrigendum 2022: budget test $CASE finished" renatob@caltech.edu
