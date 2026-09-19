#!/bin/bash
#SBATCH -A ccsi -p batch -N 1 -n 4 --mem=48G -t 08:00:00 -J eval2022_watchdog --exclude=or-condo-c[196-299] --output=/home/braghiere/ELM-FUN-2022-corrigendum/runs/logs/eval_watchdog.%j.out
cd /home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022; L=run_eval_1994-2005.log
while true; do
  grep -q "=== done" $L && { echo "driver finished on its own $(date)"; exit 0; }
  age=$(( $(date +%s) - $(stat -c %Y $L) ))
  if [ $age -gt 1500 ]; then echo "log idle ${age}s without completion -> re-running the driver here $(date)"; ./run_eval.sh 1994-2005; exit $?; fi
  sleep 120
done
