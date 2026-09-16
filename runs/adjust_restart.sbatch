#!/bin/bash
#SBATCH -A ccsi -p batch -N 1 -n 1 --mem=32G -t 02:00:00 -J adjrst
# AD -> FN handoff exactly as the 2020 chain did: replace instantaneous AD-restart pools with the 20-yr means
# from the AD h1 at year 261 (DEADSTEM/DEADCROOT C,N,P; vertically-resolved CWD/SOIL pools). Backs up the restart as .orig.
# Usage: sbatch adjust_restart.sbatch <AD_casename> <runroot>
AD=$1; RR=$2
source /etc/profile.d/modules.sh 2>/dev/null; module load python/3.10.14 2>/dev/null
export PATH=/home/braghiere/bin:/sw/cades-open/python/3.10.14/bin:$PATH
cd /home/braghiere/elm_fun_trendy_2022/OLMT
ls $RR/$AD/run/$AD.clm2.r.0261-01-01-00000.nc $RR/$AD/run/$AD.clm2.h1.0261-01-01-00000.nc || { echo "missing restart/h1 for adjust_restart"; exit 2; }
python adjust_restart.py --rundir $RR/$AD/run/ --casename $AD --restart_year 261 && echo "adjust_restart OK $(date)"
