#!/bin/bash
#SBATCH -A ccsi -p batch --nodes=12 --ntasks-per-node=32 --exclusive --mem=0 --time=10-00:00:00 --exclude=or-condo-c[196-299]
#SBATCH --job-name=corr22abc_TRc --output=/home/braghiere/ELM-FUN-2022-corrigendum/runs/logs/corr22abc_TRc.%j.out --mail-user=renatob@caltech.edu --mail-type=END,FAIL
source /etc/profile.d/modules.sh 2>/dev/null; module purge; module load python/3.10.14 2>/dev/null
export PATH=/home/braghiere/bin:/sw/cades-open/python/3.10.14/bin:$PATH
export TMPDIR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/tmp_build
source /home/braghiere/ELM-FUN-2022-corrigendum/runs/mpi_env.sh
cd /home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts/corr22abc_f19_f19_ICB20TRCNPRDCTCBC || exit 1
echo "START TR corr22abc_f19_f19_ICB20TRCNPRDCTCBC $(date)"; ./case.submit --no-batch; rc=$?
RUNDIR=$(./xmlquery --value RUNDIR); L=$(ls -t $RUNDIR/cpl.log.* 2>/dev/null | head -1)   # coupler log carries SUCCESSFUL TERMINATION
if [ $rc -eq 0 ] && ! zcat -f "$L" 2>/dev/null | tr -d "\000" | grep -q "SUCCESSFUL TERMINATION"; then echo "MODEL DID NOT TERMINATE SUCCESSFULLY (see $L)"; rc=3; fi
echo "END TR rc=$rc $(date)"
# success criterion: the expected restart exists
exit $rc
