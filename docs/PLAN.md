# Plan & status (started 2026-09-16)

## Provenance of the published product
- Output: `ELM_FUNP.clm2.h0.185001-201012.nc`, netCDF `case_id = fix_global_v6_funp_f19_f19_ICB20TRCNPRDCTCBC`, created 2020-08-29 on CADES.
- Transient branched from `fix_global_v2_f19_f19_ICB1850CNPRDCTCBC.clm2.r.0541-01-01-00000.nc` (final spin-up started year 261 => 280 yr FN). v6's own spin-up job was cancelled after 90 s and never ran.
- `use_fun=.true., use_funp=.true.`, paramfile `clm_params_c200626.nc` (s_fix=-6), CO2 diagnostic (`fco2_datm_1765-2007`), Ndep `fndep_clm_rcp4.5_simyr1849-2106_1.9x2.5`, aerosol rcp4.5, GSWP3 v2 `cpl_bypass_full`, 576 tasks / 18 nodes.
- Source that built it: `models_v3.2/E3SM_global/components/clm/src/biogeochem/CNFUNMod.F90` (180937 B, 2020-09-23) == `elm_fun_trendy_2022/.../CNFUNMod.F90` (byte-identical).
- All original run dirs/restarts were on `/lustre/or-hydra` (purged). Inputs & forcing survive on `/lustre/or-scratch/cades-ccsi/proj-shared/project_acme/e3sm_inputdata`.

## Source versions (md5)
- ORIGINAL                a2f2674b283d4b89ff486f7a69a31fd2
- + AM/EcM diag only      d0c2fef5c942ae435ad8b3646e7f95f6   (CONTROL chain)
- + bugfix only           af3190792e165768117c3e6c7363117d
- + bugfix AND diag       3eef642f9b2ef5a21cbda29760e1acbb   (CORRECTED chain)
Corrected-vs-control differs by exactly 6 diff lines (3 physics lines).

## Steps
1. [x] Recover protocol, inputs, forcing, source; build fix + diag patches; verify on copies.
2. [x] P1: port working `cades` CIME config (silent tree, built 2026-07-23) into trendy tree; originals kept as `*.orig_20260916`.
3. [ ] Compile test (trendy tree + ported config, gnu/openmpi, gcc 12.2.0).  <- go/no-go for P1; fallback P2 = build in silent tree with SourceMods.
4. [ ] OLMT create both chains (`--no_submit`), inspect namelists, then submit with SLURM afterok chaining + per-phase email.
5. [ ] Runs: 701 model-yr per chain, both in parallel (36 nodes). ETA at 150-300 yr/day: ~2.5-5 days.
6. [ ] Auto analysis: control vs corrected — mycorrhizal/non-myc/fixation C partition, AM/EcM split, NPP, C & N pools, by biome; figures; report emailed.
7. [ ] Decide corrigendum.
