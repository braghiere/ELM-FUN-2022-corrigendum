#!/bin/bash
# Event stream for the corrigendum runs: job state changes (all terminal states), hourly throughput of the running
# ELM job (from lnd.log "Beginning timestep"), and model errors. Reads job ids from runs/jobids.txt each cycle.
RR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/runs; J=/home/braghiere/ELM-FUN-2022-corrigendum/runs/jobids.txt
declare -A prev; declare -A errseen; lastrep=0; declare -A st0 t0
while true; do
  ids=$(grep -o "[A-Z0-9]*=[0-9]\+" $J | sort -u)
  for kv in $ids; do tag=${kv%%=*}; id=${kv##*=}
    s=$(squeue -j $id -h -o %T 2>/dev/null); [ -z "$s" ] && s=$(sacct -j $id -X -n -o State 2>/dev/null | head -1 | tr -d ' ')
    [ -z "$s" ] && continue
    if [ "${prev[$id]}" != "$s" ]; then echo "job $id ($tag): $s $(date +%m-%d_%H:%M)"; prev[$id]=$s; fi
  done
  now=$(date +%s)
  for d in $RR/corr22*/run; do
    L=$(ls -t $d/lnd.log.* 2>/dev/null | head -1); [ -z "$L" ] && continue
    case=$(basename $(dirname $d)); age=$(( now - $(stat -c %Y $L) )); [ $age -gt 900 ] && continue   # only logs updated in last 15 min
    n=$(tr -d "\000" < $L | grep -c "Beginning timestep")
    if [ -z "${st0[$case]}" ] || [ "${t0[$case]}" -lt $((now-3600)) ]; then
      if [ -n "${st0[$case]}" ]; then dt=$((now-${t0[$case]})); ds=$((n-${st0[$case]})); [ $dt -gt 0 ] && echo "throughput $case: $ds steps in ${dt}s = $(( ds*86400/dt/8760 )) sim-yr/day; model time $(tr -d "\000" < $L | grep "Beginning timestep" | tail -1 | grep -o '[0-9 ]*$' | tr -s ' ') $(date +%m-%d_%H:%M)"; fi
      st0[$case]=$n; t0[$case]=$now
    fi
    E=$(ls -t $d/e3sm.log.* 2>/dev/null | head -1)
    for f in $L $E; do m=$(grep -i -m1 "ENDRUN\|ERROR:\|abort\|MPI_ABORT\|Segmentation\|balance error" $f 2>/dev/null); if [ -n "$m" ] && [ -z "${errseen[$f]}" ]; then echo "MODEL ERROR in $(basename $f) ($case): ${m:0:150}"; errseen[$f]=1; fi; done
  done
  sleep 120
done
