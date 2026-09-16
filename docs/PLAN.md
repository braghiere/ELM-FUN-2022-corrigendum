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

## NEW FINDING (2026-09-16): a third defect in the published product — Defect C
While classifying tree diffs: in the 2022 `CNFUNMod.F90` `fun_cost_fix`, the paramfile-based assignment
(`s_fix*(exp(a+b*T*(1-0.5T/c))-2)`) is followed by a LIVE hardcoded line
`fun_cost_fix = (-1*(-30.0))/(1.25*exp((-3.62)+(-0.27)*T*(1-0.5*T/25.14)))` that overwrites it:
**s_fix = -30 and the temperature coefficient sign-flipped (b = -0.27)**. `fun_cost_fix` is the only fixation-cost
routine in that source (no Bytnerowicz variants). Effect: fixation cost ~900 gC/gN at 0 C rising to ~10^4-10^5 at
tropical soil T -> symbiotic fixation switched off globally.
Empirical confirmation from the published h0 (2001-2010): realized ΣNPP_NFIX/ΣNFIX = **3,884 gC/gN**; global
symbiotic NFIX = **0.000 kg N/ha/yr**; 1 of 5,663 vegetated cells > 0.01. The BNFMIP variants had this line
commented, so the BNFMIP runs were not affected; the 2022 global product was.
Also: with use_fun & use_funp both on, the 2022 tree books `ar += 0.5*soilc_change + 0.5*soilc_change_p`, i.e.
HALF of the N+P acquisition C cost is treated as autotrophic respiration (reported NPP excludes half the FUN cost;
the other half is exported to soil). Relevant to any "fraction of NPP" comparison (Ashley).
**Scope decision needed (user):** corrected chain = A+B only (as approved) vs A+B+C. Control chain must keep C
(faithful 2022 reproduction) and its build is proceeding.
- **Fidelity closure (2026-09-16):** trendy vs actual-2022 tree differ in 5 `clm/src` files (0 in `clm/bld`).
  The 2022 tree books the FULL FUN N+P cost into AR (`ar += soilc_change; ar += soilc_change_p`); trendy's 0.5/0.5 form
  is a 2023 edit. Staged the 2022 versions of CNCarbonFluxType, VegetationDataType, ColumnDataType and
  EcosystemBalanceCheckMod into BOTH chains' SourceMods so compiled physics == 2022 (BeTR ODEMod compile fix kept).
  Consequence for Ashley: reported NPP excludes the FUN cost; comparable denominator = NPP+NPP_NUPTAKE+NPP_PUPTAKE (README fixed).
- **P1 compile test PASSED** (AD case, 2026-09-16 16:24). AD case must be rebuilt once with the 4 fidelity SourceMods.
- **2026-09-16 16:42 CONTROL CHAIN SUBMITTED** (OLMT-style wrappers, BATCH_SYSTEM=none + case.submit --no-batch inside
  18-node allocations; 3-day walltime; REST_N=20; DOUT_S=FALSE; afterok chain AD -> adjust_restart -> FN -> TR; SLURM mail
  END/FAIL). Job IDs: corr22ctl AD=5684716 ADJ=5684717 FN=5684718 TR=5684719 2026-09-16. Launch mechanics note: OLMT sets BATCH_SYSTEM=none and TR shares FNs
- **2026-09-16 16:42 CONTROL CHAIN SUBMITTED.** OLMT-style wrappers (BATCH_SYSTEM=none + `case.submit --no-batch` inside
  18-node allocations), 3-day walltime, REST_N=20, DOUT_S=FALSE, afterok chain AD -> adjust_restart -> FN -> TR, SLURM mail
  on END/FAIL. Job IDs: AD=5684716 ADJ=5684717 FN=5684718 TR=5684719. Launch-mechanics notes: OLMT sets BATCH_SYSTEM=none;
  TR shares FN's executable (EXEROOT corrected to `.../corr22ctl_f19_f19_ICB1850CNPRDCTCBC/bld`; identical SourceMods+Macros).
- A+B corrected chain (`corr22fix`, srcmods_fix) being created+built in background; NOT submitted pending scope decision
  (A+B vs A+B+C vs three chains). srcmods_fixABC staged.
- Verified `histFileMod::set_hist_filename` stamps averaged (nhtfrq<0) history files with the CURRENT date at write time,
  so the AD h1 covering years 241-260 is `…clm2.h1.0261-01-01-00000.nc` — exactly what `adjust_restart.py --restart_year 261`
  reads (same as the 2020 chain). Persistent monitor armed on the AD job (first step / errors / hourly throughput / terminal state).
- **Throughput reality check (2026-09-16 16:49):** lnd.log prints one line per hourly timestep; first ~5 min gave ~60-65 sim-yr/day
  at 576 tasks (not the 150-300 assumed from f09 logs). AD 260 yr ~4.2 d, FN 280 ~4.5 d, TR 161 ~2.6 d -> ~11 days per chain
  (chains run in parallel). Cancelled the 3-day-walltime control jobs (5684716-19, 6 min lost) and resubmitted with 10-day
  walltime: corr22ctl AD=5684721 ADJ=5684722 FN=5684723 TR=5684724 2026-09-16. Will refine ETA from the hourly monitor.
- **2026-09-16 16:51 A+B CHAIN SUBMITTED** (srcmods_fix; FN/TR share the AD executable — Macros identical across AD/FN/TR,
  same pattern validity as control). Job IDs: AD=5684725 ADJ=5684726 FN=5684727 TR=5684728.
- **Scheduler constraint:** A+B AD is PENDING with reason `MaxCpuPerAccount` while the control AD (576 CPUs) runs -> the
  `ccsi` account cap likely prevents two 576-task jobs concurrently. If so, chains run SEQUENTIALLY (~11-12 d each at
  ~55-65 sim-yr/day). Options under evaluation: (a) accept sequential; (b) fewer tasks per chain to fit two under the cap
  (throughput per chain drops, but parallel); (c) burst partition with 2-day chunked restarts (REST_N=20 supports it).
- **SCOPE DECISION (user, 2026-09-16 ~17:00): ALL corrections bundled — A (param swap) + B (PFT typo) + C (s_fix override
  removed), exactly as the BNFMIP fix. Two chains: control vs corrected(ABC). A+B-only chain cancelled (jobs 5684725-28, never ran).**

## 2026-09-16 (evening) — protocol correction: FUN-off shared spin-up, bundled A+B+C, MPI transport
**Scope (user):** the corrected chain bundles ALL three fixes (A param swap, B PFT typo, C s_fix override) exactly as in
BNFMIP — `runs/srcmods_fixABC` (CNFUNMod md5 eae819ff). A+B-only chain (`corr22fix`) cancelled before it ran; its AD case
is reused only as a 384-task scaling probe (FUN off ⇒ code path identical).

**Spin-up FUN status — verified, and it changes the design.** The published transient `fix_global_v6_funp` branched from
`fix_global_v2_f19_f19_ICB1850CNPRDCTCBC.clm2.r.0541` (FN, RUN_STARTDATE 0001, so 540 FN years) which itself came from the
v2 AD `r.0261` (260 yr). The v2 spin-up cases have **no `use_fun`/`use_funp`** in `user_nl_clm`; the model default is
`.false.` (`clm_varctl.F90:330-331`; build-namelist has no non-FATES default) and the surviving v3 AD h0 has NPP_NUPTAKE =
NPP_NACTIVE = NPP_NFIX ≡ 0 in every cell. **The published spin-up ran FUN off; FUN/FUN-P were switched on at 1850 in the
transient.** All three 2022 products (ELM = v3, ELM_FUN = v3_fun, ELM_FUNP = v6_funp) are transients off that same restart.
Other v2-vs-v6-template differences: v2 spin-up had `use_lch4 = .true.` (v6 TR: `.false.`), RCP4.5 co2_file (inert:
`co2_type='constant'` 284.7 ppm), OLMT-staged `clm_params_c180524.nc` — which equals `c200626` in all 294 shared parameters
(c200626 only adds the 26 FUN entries that the 2022 `readParamsMod` reads unconditionally). Consequences:
- The control AD that had been running (FUN-P on, lch4 off, from v6 templates) was unfaithful → cancelled at 15 min; logs kept
  in `run/abandoned_funon_20260916/`.
- New templating `runs/apply_namelists.py`: AD/FN from `runs/v2_spinup_namelists/` (v2 ground truth), TR from v6;
  FN = 540 yr; TR finidat = FN `r.0541`. Verified in resolved `lnd_in`: AD/FN have no use_fun (default off), use_lch4 T;
  TR use_fun/use_funp T, use_lch4 F, finidat r.0541.
- **One shared FUN-off spin-up (corr22ctl AD 260 + FN 540) feeds both transients** — the A/B/C fixes cannot touch a FUN-off
  run. Work drops from 2×801 to 800 + 2×161 model-years and the 960-CPU account cap stops mattering for the long phase.
- Source tree: the 2020 spin-up ran in `E3SM_latest/E3SM` (same base b1517eec0; 45 clm/src files differ from the 2022 tree,
  FUN-related). We run everything in the single 2022 tree — same protocol, one code base; exact bit reproduction of the 2020
  state was never possible (or-hydra scratch and its restarts are gone; compilers changed).

**Throughput — the 2020 record vs ours.** CaseStatus: v2 AD 260 yr in 11.4 h (~550 sim-yr/day, 384 tasks, FUN off);
v6_funp TR 161 yr in 9.0 h (~430 sim-yr/day, FUN-P on). Ours: 35–55 sim-yr/day at 576 tasks. Flags are the same (`-O`,
DEBUG=FALSE). Diagnosis: `openmpi/4.1.6` has only tcp/vader/self BTLs; its `pml_ucx` links spack UCX 1.16 with
rc_verbs/ud_verbs on mlx4_0. Fix applied: `runs/mpi_env.sh` (OMPI_MCA_pml=ucx, osc=ucx, btl=^tcp,openib, UCX_TLS=^ud)
sourced by every wrapper; `--cpu-bind=none` → `--cpu-bind=cores` in config_machines and in each case's env_mach_specific.xml.
First AD job runs with UCX_LOG_LEVEL=info to record the transport actually used. A 384-task, 1-month probe (12 nodes) runs
alongside to pick the transient layout (576+384 = 960 = account cap).

**Submitted:** shared spin-up AD 5684744 → adjust_restart 5684745 → FN 5684746 (`runs/submit_spinup.sh corr22ctl`).
Transients: `runs/submit_transient.sh corr22ctl <FN>` and `... corr22abc <FN>` once the abc build finishes
(`runs/olmt_create_abc.log`); report: `runs/submit_report.sh <TRctl> <TRabc>`. Monitor: `runs/monitor_chain.sh`.

### 2026-09-16 ~18:00 — FUN-off carbon balance does not close in the 2022 tree → spin-up moves to the frozen 2020 tree
- First faithful spin-up job (5684744, FUN off, lch4 on, 576 tasks, UCX/IB confirmed: `inter-node rc_verbs/mlx4_0`) ran at
  **3 sim-yr/day**: from model day 11 the balance check printed `column cbalance error` (|err| 1e-7…4e-5 gC/m²/step) for 577
  columns at every step — 292k lines in 11 min from 576 ranks. Cancelled; logs in `run/abandoned_cbal_flood_20260916/`.
- Cause is in the 2022 `EcosystemBalanceCheckMod` (SourceMods fidelity file, mtime 2020-08-23): threshold raised 1e-8→1e-7,
  `endrun` **commented out** when FUN is off, and the whole diagnostic block **skipped** when FUN is on (so FUN-on runs never
  report balance errors at all). The 2020 tree that produced the published spin-up (`E3SM_latest/E3SM`, newest source
  2020-06-10 = the day v2 was created and submitted) still has `endrun` at 1e-8 → its FUN-off spin-up necessarily closed.
- Methane is not the trigger: a 1-month FUN-off, `use_lch4=.false.` test (job 5684757, 12 nodes) flooded from the first
  steps (23.7k warnings in 64 steps). The non-closure is intrinsic to the 2022 tree family in FUN-off mode (it also implies
  the 2020 FUN-off "ELM" product v3 TR — submitted 4 min after that 08-23 edit — ran with a non-closing balance).
- **Decision: run the FUN-off spin-up in the frozen 2020 tree, exactly as in 2020** (no SourceMods, `clm_params_c180524.nc`,
  384 tasks/12 nodes as v2, `use_lch4=.true.`, AD 260 → FN 540), then hand `r.0541` to the two 2022-tree FUN-P transients
  — the same 2020-tree→2022-tree restart handoff the published product used. Port = straight copy of the three machine
  XMLs (2020 files were byte-identical to the trendy originals) + the ODEMod gcc-12 fix. Chain prefix `corr22spin20`
  (`runs/olmt_create_spin20.log`). Transients (`corr22ctl`, `corr22abc`) re-pointed to `corr22spin20_…CNPRDCTCBC.clm2.r.0541`
  and switched to 384 tasks so both fit under the 960-CPU cap side by side.
- Corrigendum diagnostic to add later: enable a rate-limited FUN-on balance report in the transients (the 2022 code silently
  skips it), so we know whether the FUN-P runs conserve carbon.

### 2026-09-16 18:01 — final layout submitted
| stage | case (tree) | job | depends | length |
|---|---|---|---|---|
| shared FUN-off AD | `corr22spin20_…CNRDCTCBC_ad_spinup` (frozen 2020 tree `E3SM_latest/E3SM`) | 5684763 | — | 260 yr, 384 tasks / 12 nodes |
| adjust_restart | OLMT `adjust_restart.py` on AD `r.0261` (20-yr means from h1) | 5684764 | afterok AD | — |
| shared FUN-off FN | `corr22spin20_…CNPRDCTCBC` (2020 tree) | 5684765 | afterok ADJ | 540 yr → `r.0541` |
| control transient (FUN-P on, 2022 code as published) | `corr22ctl_…ICB20TRCNPRDCTCBC` (2022 tree, srcmods_ctl d0c2fef5) | 5684766 | afterok FN | 1850–2010, 384 tasks |
| corrected transient (A+B+C bundled) | `corr22abc_…ICB20TRCNPRDCTCBC` (2022 tree, srcmods_fixABC eae819ff) | 5684767 | afterok FN | 1850–2010, 384 tasks |
| analysis + email | `runs/final_report.sbatch` (control vs corrected vs published) | 5684768 | afterok both TR | — |
Both transients use byte-identical namelists apart from the case name (verified), `use_fun/use_funp=.true.`, `use_lch4=.false.`,
`clm_params_c200626.nc`, finidat = spin20 FN `r.0541`. Spin-up namelists are the v2 files verbatim modulo paths
(`clm_params_c180524.nc`, `use_lch4=.true.`, no FUN). Superseded cases kept (not deleted): `corr22ctl` AD/FN (2022 tree),
`corr22fix` (A+B), `corr22spin20` TR (unused).

### 2026-09-16 18:16 — throughput root cause: UCX was using the 10 GbE port, not InfiniBand
The 2020-tree spin-up (job 5684763) closed the carbon balance (0 warnings) but still ran at **8 sim-yr/day**. gdb stack
samples on four nodes: every rank in `MPI_Waitall` inside the MCT rearranger of the coupler exchange (`cime_run_lnd_recv_post`),
UCX progressing a **TCP** interface. `ibstat` on the compute nodes: `mlx4_0` **port 1 = InfiniBand 56 Gb (Active)**, **port 2 =
Ethernet 10 Gb**. UCX had auto-selected `rc_verbs/mlx4_0:2` (RoCE over the lossy 10 GbE port) + `tcp/ib0` as inter-node lanes.
Fix (both trees' `config_machines.xml`, every case's `env_mach_specific.xml`, `runs/mpi_env.sh`): `UCX_NET_DEVICES=mlx4_0:1`,
`UCX_TLS=rc_verbs,ud_verbs,sm,self` (replacing the inherited `UCX_TLS=^ud`). Chain cancelled and resubmitted:
AD 5684779 → ADJ 5684780 → FN 5684781 → TR ctl 5684782 / TR abc 5684783 → report 5684784. Two-node ping-pong benchmark
(`scratch pp.c`, results below) quantifies the transports.
