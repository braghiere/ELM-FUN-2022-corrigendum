#!/bin/bash
#SBATCH -A ccsi -p batch --nodes=12 --ntasks-per-node=32 --exclusive --mem=0 --time=02:00:00
#SBATCH --job-name=corr22_test_lch4off --output=/home/braghiere/ELM-FUN-2022-corrigendum/runs/logs/test_lch4off.%j.out --mail-user=renatob@caltech.edu --mail-type=FAIL
# Scaling probe: 1 model month of the FUN-off AD spin-up at 384 tasks (12 nodes), same exe class, to compare steps/s with the 576-task production AD.
source /etc/profile.d/modules.sh 2>/dev/null; module purge; module load python/3.10.14 2>/dev/null
export PATH=/home/braghiere/bin:/sw/cades-open/python/3.10.14/bin:$PATH
export TMPDIR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/tmp_build
source /home/braghiere/ELM-FUN-2022-corrigendum/runs/mpi_env.sh
cd /home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts/corr22fix_f19_f19_ICB1850CNRDCTCBC_ad_spinup || exit 1
./xmlchange STOP_OPTION=nmonths,STOP_N=1,REST_OPTION=nyears,REST_N=20,RUN_STARTDATE=0001-01-01,DOUT_S=FALSE,RESUBMIT=0,CONTINUE_RUN=FALSE
echo "START probe384 $(date)"; ./case.submit --no-batch; rc=$?; echo "END probe384 rc=$rc $(date)"; exit $rc
