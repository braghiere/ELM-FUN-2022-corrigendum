#!/bin/bash
# Restart a transient from its latest restart with the CO2 file that covers 2006-2010 (the 2020 transient's file ends in 2007 and
# the model reads past it: PCO2 -> 0 by mid-2010 in all archived products). Usage: continue_transient.sh <prefix> <restart_year e.g. 1910>
set -e; P=$1; Y=$2; CR=/home/braghiere/elm_fun_trendy_2022/E3SM_global/cime/scripts; C=$CR/${P}_f19_f19_ICB20TRCNPRDCTCBC
RR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/runs/${P}_f19_f19_ICB20TRCNPRDCTCBC/run; export PATH=/home/braghiere/bin:/sw/cades-open/python/3.10.14/bin:$PATH
ls $RR/${P}_f19_f19_ICB20TRCNPRDCTCBC.clm2.r.${Y}-01-01-00000.nc >/dev/null
# point the rpointer files at the chosen restart (the run may have advanced past it)
for f in $RR/rpointer.*; do sed -i "s/\.r\.[0-9]\{4\}-01-01-00000/.r.${Y}-01-01-00000/; s/\.r\.[0-9]\{4\}-[0-9][0-9]-[0-9][0-9]-[0-9]*/.r.${Y}-01-01-00000/" $f; done
cd $C && sed -i "s|fco2_datm_1765-2007_c100614.nc|fco2_datm_rcp4.5_1765-2500_c130312.nc|" user_nl_clm && grep -q rcp4.5 user_nl_clm
./xmlchange CONTINUE_RUN=TRUE,STOP_OPTION=nyears,STOP_N=$((2011-Y)),REST_OPTION=nyears,REST_N=20,RESUBMIT=0
echo "   $P: rpointers -> r.${Y}; co2_file -> rcp4.5; CONTINUE_RUN=TRUE STOP_N=$((2011-Y))"; head -3 $RR/rpointer.lnd
