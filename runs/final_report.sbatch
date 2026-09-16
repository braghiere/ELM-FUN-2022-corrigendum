#!/bin/bash
#SBATCH -A ccsi -p batch -N 1 -n 1 --mem=64G -t 04:00:00 -J corr22_report
# Runs after ALL transient jobs complete (afterok). Args: label:h0glob ... (first = control). Emails report + figures.
source /etc/profile.d/modules.sh 2>/dev/null
R=/home/braghiere/ELM-FUN-2022-corrigendum; cd $R
/home/braghiere/miniconda3/bin/python runs/analyze_chains.py "$@" > analysis/analyze_chains.log 2>&1; rc=$?
git add -A analysis >/dev/null 2>&1; git commit -q -m "Automated end-of-run analysis: control vs corrected chains" >/dev/null 2>&1; git push -q origin main >/dev/null 2>&1
if [ $rc -eq 0 ]; then
  { echo "ELM-FUN 2022 corrigendum check: all chains finished. Report attached (also in repo analysis/CHAIN_REPORT.md)."; echo; cat analysis/CHAIN_REPORT.md; } \
   | mail -s "[ELM-FUN 2022 corrigendum] RESULTS: control vs corrected" -a analysis/figs/chains_biome_bars.png -a analysis/figs/chains_maps_delta.png renatob@caltech.edu
else
  { echo "Analysis FAILED (rc=$rc). Log:"; tail -40 analysis/analyze_chains.log; } | mail -s "[ELM-FUN 2022 corrigendum] analysis FAILED — waiting for input" renatob@caltech.edu
fi
