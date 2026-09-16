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

## Execution log
- 2026-09-16 P1 config port done (backups `*.orig_20260916`); diffs confined to `cades` blocks (+2 blank lines).
- Overlay inputdata: `/lustre/or-scratch24/scratch/braghiere/corrigendum_2022/inputdata` (symlinks to shared
  e3sm_inputdata; real dirs for ndepdata/paramdata/CO2/aero). Generated constant-1850 Ndep/aero/CO2 streams
  (`ncks` slices, verified YEAR=1850 / date=1850xx / CO2=284.7 ppm) — kept for OLMT defaults, but the v6
  baseline used the TRANSIENT stream files in all phases, so final namelists are templated from v6.
- v6 ground-truth `user_nl_clm` for all 3 phases saved in `runs/v6_baseline_namelists/`; `runs/apply_v6_namelists.py`
  makes ours identical modulo paths/casenames (+ explicit hist_fincl1 with pathway fluxes & pools).
- Same paramfile for BOTH chains (`/home/braghiere/clm_params_c200626.nc`, as v6): the code overwrites the
  non-myc arrays anyway, so the only inter-chain difference is the SourceMods CNFUNMod (3 physics lines).
- CNP file: OLMT `CNP_parameters_c180529.nc` (md5 e7efc1a5…) == the copy every OLMT here has used. Consistent.
- Python: `~/bin/python` -> 3.10.14 (module) runs both OLMT (numpy/netCDF4) and 2022-era CIME. miniconda 3.13 breaks CIME.
- Compile test launched: control chain, `global_fullrun.py --no_submit` (log `runs/olmt_create_ctl.log`).
- First OLMT attempt failed at `runcase.py:896`: in this OLMT `--parm_file` is a *text parameter-modification
  list* opened from the OLMT dir; the netCDF paramfile option is `--mod_parm_file <path>` (passed through by
  `global_fullrun.py`; ncap edits only fire for humhol/marsh). Relaunched with `--mod_parm_file`.
- makepointdata built f19 inputs from the overlay: domain `domain.lnd.fv1.9x2.5_gx1v6.090206.nc`, 17-PFT
  `surfdata_1.9x2.5_simyr1850_c180306.nc`, dynpft from `landuse.timeseries_1.9x2.5_rcp8.5_simyr1850-2100_c141219.nc`
  (OLMT's hardcoded f19 default in makepointdata.py:98 — kept, as the 2020 tool used the same logic; identical across chains).
- Post-creation: `runs/verify_cases.sh <prefix>` (templates v6 namelists, checks all .nc paths, env, SourceMods md5,
  normalized diff vs v6). Submission: `runs/submit_chain.sh <prefix>` (one long job per phase, afterok chaining,
  email END/FAIL to renatob@caltech.edu). Neither run yet.
- **Compile test failure #1 (P1) — root cause & fix.** PIO's cmake probes failed with
  `undefined reference to H5Pset_dxpl_mpio …` -> `size_t and long long must be the same size!`.
  Cause: the spack `netcdf-c-4.9.2-mpi-h5f` library links *parallel* HDF5; cmake's `try_compile` links only
  `libnetcdf.so`, and GNU ld resolves its NEEDED `libhdf5.so.310` via `LD_LIBRARY_PATH` (which the cades config
  puts `~/miniconda3/lib` first on) *before* the library's own RUNPATH -> binds to miniconda's **serial** HDF5 ->
  MPI symbols missing. The July/Sept-8 silent-tree build passed because its PIO cache had
  `CMAKE_EXE_LINKER_FLAGS=-L<hdf5>/lib -lhdf5_hl -lhdf5 -lz -ldl -lm`, seeded by an `LDFLAGS` **exported by hand
  in that shell** (present in no config or script; the July recipe omitted it). Fix (tracked): add
  `<env name="LDFLAGS">-L$ENV{OLCF_HDF5_ROOT}/lib -lhdf5_hl -lhdf5 -lz -ldl -lm</env>` to the `cades` machine block
  (`config_machines.xml`; pre-fix copy kept as `*.ported_prefix_20260916`). Relaunched (RELAUNCH-3).
- Note for later: July case Macros used `-mcmodel=medium`; current config gives `small`. If the global link hits
  "relocation truncated to fit", switch CFLAGS to `-mcmodel=medium`.
- **Compile test failure #2 (P1)** — model compile stopped at 46% in the BeTR external
  (`sbetr/.../ODEMod.F90:672`, "Explicit interface required for polymorphic argument", gcc>=10 strictness).
  Only 5 files differ between the trendy and silent `components/clm/src`; the silent tree's BeTR fix is all
  `call odefun(...)` lines commented out (36 lines). BeTR is not enabled in this compset (v6 lnd_in has no
  `use_betr`), so this is compile-only dead code for our runs. Ported that file (original kept as
  `ODEMod.F90.orig_20260916`); other 4 diffs are BNFMIP-era FUN/diagnostic changes and are NOT ported (fidelity).
  Rebuilding the AD case directly (`case.build`, log `runs/casebuild_ctl_ad.log`) as the compile test.
- CIME writes `export LDFLAGS=<value with spaces>` unquoted into `.env_mach_specific.sh` (only affects manual
  sourcing; the real build takes env from the XML — PIO cache confirmed the full flags).
