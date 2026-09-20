#!/bin/bash
# Generate OLMT-style SBATCH wrappers (case.submit --no-batch inside an 18-node allocation) for one chain.
# Usage: make_wrappers.sh <prefix>   -> runs/wrappers/<prefix>_{AD,FN,TR}.sbatch
P=$1; CR=/home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts; [ "$P" = corr22spin20 ] && CR=/home/braghiere/E3SM_latest/E3SM/cime/scripts; W=/home/braghiere/ELM-FUN-2022-corrigendum/runs/wrappers; LG=/home/braghiere/ELM-FUN-2022-corrigendum/runs/logs
MAIL=renatob@caltech.edu
gen(){ # $1 tag $2 casename $3 STOP_N $4 RUN_STARTDATE
NT=$(grep -o 'compclass="LND">[0-9]*' $CR/$2/env_mach_pes.xml | head -1 | grep -o '[0-9]*$'); NODES=$(( (NT+31)/32 ))
cat > $W/${P}_$1.sbatch <<EOF
#!/bin/bash
#SBATCH -A ccsi -p batch --nodes=$NODES --ntasks-per-node=32 --exclusive --mem=0 --time=10-00:00:00 --exclude=or-condo-c[196-299]
#SBATCH --job-name=${P}_$1 --output=$LG/${P}_$1.%j.out --mail-user=$MAIL --mail-type=END,FAIL
source /etc/profile.d/modules.sh 2>/dev/null; module purge; module load python/3.10.14 2>/dev/null
export PATH=/home/braghiere/bin:/sw/cades-open/python/3.10.14/bin:\$PATH
export TMPDIR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/tmp_build
source /home/braghiere/ELM-FUN-2022-corrigendum/runs/mpi_env.sh
cd $CR/$2 || exit 1
./xmlchange STOP_OPTION=nyears,STOP_N=$3,REST_OPTION=nyears,REST_N=20,RUN_STARTDATE=$4,DOUT_S=FALSE,RESUBMIT=0,CONTINUE_RUN=FALSE
echo "START $1 $2 \$(date)"; ./case.submit --no-batch; rc=\$?
RUNDIR=\$(./xmlquery --value RUNDIR); L=\$(ls -t \$RUNDIR/cpl.log.* 2>/dev/null | head -1)   # coupler log carries SUCCESSFUL TERMINATION
if [ \$rc -eq 0 ] && ! zcat -f "\$L" 2>/dev/null | tr -d "\\000" | grep -q "SUCCESSFUL TERMINATION"; then echo "MODEL DID NOT TERMINATE SUCCESSFULLY (see \$L)"; rc=3; fi
echo "END $1 rc=\$rc \$(date)"
# success criterion: the expected restart exists
exit \$rc
EOF
}
gen AD ${P}_f19_f19_ICB1850CNRDCTCBC_ad_spinup 260 0001-01-01
gen FN ${P}_f19_f19_ICB1850CNPRDCTCBC          540 0001-01-01   # published transient branched from FN r.0541
gen TR ${P}_f19_f19_ICB20TRCNPRDCTCBC          161 1850-01-01
ls -1 $W/${P}_*.sbatch
