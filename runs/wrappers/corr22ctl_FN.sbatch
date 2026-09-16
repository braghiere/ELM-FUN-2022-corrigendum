#!/bin/bash
#SBATCH -A ccsi -p batch --nodes=18 --ntasks-per-node=32 --exclusive --mem=0 --time=10-00:00:00
#SBATCH --job-name=corr22ctl_FN --output=/home/braghiere/ELM-FUN-2022-corrigendum/runs/logs/corr22ctl_FN.%j.out --mail-user=renatob@caltech.edu --mail-type=END,FAIL
source /etc/profile.d/modules.sh 2>/dev/null; module purge; module load python/3.10.14 2>/dev/null
export PATH=/home/braghiere/bin:/sw/cades-open/python/3.10.14/bin:$PATH
export TMPDIR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/tmp_build
source /home/braghiere/ELM-FUN-2022-corrigendum/runs/mpi_env.sh
cd /home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts/corr22ctl_f19_f19_ICB1850CNPRDCTCBC || exit 1
./xmlchange STOP_OPTION=nyears,STOP_N=540,REST_OPTION=nyears,REST_N=20,RUN_STARTDATE=0001-01-01,DOUT_S=FALSE,RESUBMIT=0,CONTINUE_RUN=FALSE
echo "START FN corr22ctl_f19_f19_ICB1850CNPRDCTCBC $(date)"; ./case.submit --no-batch; rc=$?; echo "END FN rc=$rc $(date)"
# success criterion: the expected restart exists
exit $rc
