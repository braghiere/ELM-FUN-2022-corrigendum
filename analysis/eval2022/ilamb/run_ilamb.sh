#!/bin/bash
# ILAMB benchmark of published (ELM, ELM-FUN2.0, ELM-FUN3.0 as CMORized in 2022) and rerun (control, corrected) products, 1994-2005.
# Usage: run_ilamb.sh   (after cmorize_elm.py has produced MODELS/control and MODELS/corrected)
IR=/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/ilamb_root; cd $IR
mkdir -p MODELS; for m in ELM ELM_FUN ELM_FUNP; do [ -e MODELS/$m ] || ln -s /home/braghiere/ELM_FUN_output/ELM_output/$m MODELS/$m; done
export ILAMB_ROOT=$IR
/home/braghiere/miniconda3/bin/conda run -n ilamb ilamb-run --config /home/braghiere/ELM-FUN-2022-corrigendum/analysis/eval2022/ilamb/ilamb_elmfun.cfg \
  --model_root $IR/MODELS --models ELM ELM_FUN ELM_FUNP control corrected --study_limits 1994 2005 --regions global --build_dir $IR/_build_elmfun 2>&1 | tee $IR/ilamb_run.log
