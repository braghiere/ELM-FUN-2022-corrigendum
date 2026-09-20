#!/bin/bash
# Carbon-budget test runs (corrigendum, 2026-09-19): 2 years from the control restart r.1990 in the 2022 tree, balance check instrumented
# (runs/srcmods_cbal). T1 = FUN off, T2 = FUN-P on. Usage: submit_cbal_tests.sh cbal_funoff|cbal_funon
n=$1; CR=/home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts; CASE=corr22${n}_f19_f19_ICB20TRCNPRDCTCBC
W=/home/braghiere/ELM-FUN-2022-corrigendum/runs/wrappers; LG=/home/braghiere/ELM-FUN-2022-corrigendum/runs/logs; mkdir -p $W $LG
NT=$(grep -o 'compclass="LND">[0-9]*' $CR/$CASE/env_mach_pes.xml | head -1 | grep -o '[0-9]*$'); NODES=$(( (NT+31)/32 ))
cat > $W/corr22${n}.sbatch <<EOS
#!/bin/bash
#SBATCH -A ccsi -p batch --nodes=$NODES --ntasks-per-node=32 --exclusive --mem=0 --time=08:00:00 --exclude=or-condo-c[196-299]
#SBATCH --job-name=corr22${n} --output=$LG/corr22${n}.%j.out --mail-user=renatob@caltech.edu --mail-type=END,FAIL
source /etc/profile.d/modules.sh 2>/dev/null; module purge; module load python/3.10.14 2>/dev/null
export PATH=/home/braghiere/bin:/sw/cades-open/python/3.10.14/bin:\$PATH
export TMPDIR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/tmp_build
source /home/braghiere/ELM-FUN-2022-corrigendum/runs/mpi_env.sh
cd $CR/$CASE || exit 1
./xmlchange STOP_OPTION=nyears,STOP_N=2,REST_OPTION=nyears,REST_N=2,RUN_STARTDATE=1990-01-01,DOUT_S=FALSE,RESUBMIT=0,CONTINUE_RUN=FALSE
echo "START $n \$(date)"; ./case.submit --no-batch; rc=\$?
RUNDIR=\$(./xmlquery --value RUNDIR); L=\$(ls -t \$RUNDIR/cpl.log.* 2>/dev/null | head -1)
if [ \$rc -eq 0 ] && ! zcat -f "\$L" 2>/dev/null | tr -d "\\000" | grep -q "SUCCESSFUL TERMINATION"; then echo "MODEL DID NOT TERMINATE SUCCESSFULLY (see \$L)"; rc=3; fi
echo "END $n rc=\$rc \$(date)"; exit \$rc
EOS
sbatch $W/corr22${n}.sbatch | tee -a /home/braghiere/ELM-FUN-2022-corrigendum/runs/jobids.txt
