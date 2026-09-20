#!/bin/bash
#SBATCH -A ccsi -p batch --nodes=12 --ntasks-per-node=32 --exclusive --mem=0 --time=08:00:00 --exclude=or-condo-c[196-299]
#SBATCH --job-name=corr22cbal_funoff --output=/home/braghiere/ELM-FUN-2022-corrigendum/runs/logs/corr22cbal_funoff.%j.out --mail-user=renatob@caltech.edu --mail-type=END,FAIL
source /etc/profile.d/modules.sh 2>/dev/null; module purge; module load python/3.10.14 2>/dev/null
export PATH=/home/braghiere/bin:/sw/cades-open/python/3.10.14/bin:$PATH
export TMPDIR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/tmp_build
source /home/braghiere/ELM-FUN-2022-corrigendum/runs/mpi_env.sh
cd /home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts/corr22cbal_funoff_f19_f19_ICB20TRCNPRDCTCBC || exit 1
./xmlchange STOP_OPTION=nyears,STOP_N=2,REST_OPTION=nyears,REST_N=2,RUN_STARTDATE=1990-01-01,DOUT_S=FALSE,RESUBMIT=0,CONTINUE_RUN=FALSE
echo "START cbal_funoff $(date)"; ./case.submit --no-batch; rc=$?
RUNDIR=$(./xmlquery --value RUNDIR); L=$(ls -t $RUNDIR/cpl.log.* 2>/dev/null | head -1)
if [ $rc -eq 0 ] && ! zcat -f "$L" 2>/dev/null | tr -d "\000" | grep -q "SUCCESSFUL TERMINATION"; then echo "MODEL DID NOT TERMINATE SUCCESSFULLY (see $L)"; rc=3; fi
echo "END cbal_funoff rc=$rc $(date)"; exit $rc
