#!/bin/bash
# clean rebuild with -DCPL_BYPASS restored, then submit the budget test and arm its analysis waiter
n=$1; CR=/home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts; C=$CR/corr22${n}_f19_f19_ICB20TRCNPRDCTCBC
source /etc/profile.d/modules.sh; module purge; module load python/3.10.14; export TMPDIR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/tmp_build
cd $C && ./case.build --clean-all > /dev/null 2>&1; ./case.build > /home/braghiere/ELM-FUN-2022-corrigendum/runs/casebuild_${n}.log 2>&1
if grep -q "MODEL BUILD HAS FINISHED SUCCESSFULLY" /home/braghiere/ELM-FUN-2022-corrigendum/runs/casebuild_${n}.log && zgrep -q "DCPL_BYPASS" $(./xmlquery --value EXEROOT)/e3sm.bldlog.* ; then
  J=$(/home/braghiere/ELM-FUN-2022-corrigendum/runs/submit_cbal_tests.sh $n | grep -o "[0-9]*$")
  echo "$(date) $n rebuilt with CPL_BYPASS, submitted job $J" >> /home/braghiere/ELM-FUN-2022-corrigendum/runs/logs/rebuild_cbal.log
  nohup /home/braghiere/ELM-FUN-2022-corrigendum/analysis/cbal/wait_and_analyze.sh $J corr22${n}_f19_f19_ICB20TRCNPRDCTCBC > /dev/null 2>&1 &
else
  echo "$(date) $n BUILD FAILED or CPL_BYPASS missing" >> /home/braghiere/ELM-FUN-2022-corrigendum/runs/logs/rebuild_cbal.log
fi
