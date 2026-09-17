# Re-plot of Ashley's ELM-FUN comparison with the correct variable (2026-09-16)

**What she plotted (panel A):** `COST_NACTIVE + COST_PACTIVE` from the FUN-P extracts. In the code these are
`cost_nactive = Nactive/npp_Nactive` (gN/gC) and `cost_pactive = Pactive/npp_Pactive` (gP/gC) — uptake
*efficiencies*, not carbon fluxes. Their sum has mixed units and is not "C allocation"; the y-axis label
"gC/m2/yr" on her figures is therefore incorrect. The apparent boreal 1:1 "match" is a numerical coincidence.

**Correct variable (panel B):** `NPP_NACTIVE + NPP_PACTIVE` (gC/m2/s -> gC/m2/yr): carbon actually spent on
mycorrhizal (AM+EcM) N and P uptake; excludes non-mycorrhizal uptake.
**Denominator (verified in the 2022 build source, 2026-09-16):** with FUN and FUN-P on, the 2022 tree books the
FULL N+P acquisition cost into autotrophic respiration (`ar += soilc_change + soilc_change_p`), so the reported
`NPP` = GPP - AR_base - (NPP_NUPTAKE + NPP_PUPTAKE) EXCLUDES the FUN cost. The quantity comparable to a
satellite/total NPP is therefore `NPP + NPP_NUPTAKE + NPP_PUPTAKE`; use `(NPP_NACTIVE+NPP_PACTIVE)/(NPP+NPP_NUPTAKE+NPP_PUPTAKE)`
(stored as `pct_gross` in replot_data.json). Earlier drafts said the cost sat inside NPP — that was wrong. Do NOT use
`NUPTAKE_NPP_FRACTION` as "fraction of NPP": its denominator is `AVAILC` = GPP - maintenance respiration.

**ELM source:** `fix_global_v6_funp_f19_f19_ICB20TRCNPRDCTCBC` (the 2022 JAMES product), 2001-2010 mean,
grid cells classified by dominant natural PFT (>30% of vegetated fraction) with NPP > 100 gC/m2/yr,
area-weighted; bars = p10-p90. Group->PFT map: AM crops 15,16; AM grasses 13,14; AM trees/shrubs 4,5,6;
EcM broadleaf 8-11; EcM needleleaf 1,2,3 (deciduous needle = 3; evergreen needle = 1,2); PFT 7 (BDT temperate)
is 50/50 in ELM and shown separately. ELM has no needleleaf-shrub PFT.

**Ashley's x-values** are her group summary markers read visually from her figures (approx +-3 gC/m2/yr);
pixel-level points cannot be recovered from the images.

**Caveats on the ELM side (important):**
- AM/EcM split variables (`NPP_NAM/NECM/PAM/PECM`) are identically zero in the published output (declared,
  never assigned). Only total mycorrhizal C is available. ELM's AM/EcM assignment is a hardcoded per-PFT
  constant (0.99 EcM / 0.01 AM / 0.50 for PFT 7), not a spatial MFT map.
- The 2022 source carries two inherited FUN defects (hardcoded, so paramfile-independent):
  (A) non-myc kc/kn swapped orientation in the live tier (CTSM #2120 lineage); (B) `ivt.eq.7` typo that puts
  PFT 7 (temperate broadleaf deciduous) in the C4-grass/corn active-cost tier. **Re-examined 2026-09-16 (evening):** in the 2022 code the swap (A) sits only in the PFT 3 (larch) tier (all other tiers have
  kc = kn, so a swap is a no-op), the PFT 7 typo (B) is numerically inert (the wrong tier has the same 0.025/0.050 values as the
  default), and the fixation fix (C) makes fixation 7-12 gC/gN, still ~10x dearer than ELM's mycorrhizal uptake (0.16-0.86 gC/gN
  area means). Expected effect of the corrections on mycorrhizal C: small, slightly downward (larch; N-poor cells). The earlier
  'lower bound' statement is withdrawn. The BNFMIP site shifts (Manaus 0.7->10.8, Harvard 0.3->8.2 gC/m2/yr from A+B) came from a
  newer code with the swap in ALL PFTs and do not transfer.
- Boreal soil mineral N over-accumulates in ELM (known), which cheapens N uptake and likely depresses boreal
  mycorrhizal allocation (2.1% of NPP).
- AM natural grasses come out very high (~108 gC/m2/yr, ~34% of NPP) — flag, not yet explained.
- Single deterministic run; no uncertainty layers exist.

Files: replot_hyphal_vs_ELM_corrected.png, replot_data.json (her x reads + ELM per-group stats).

## Verified numbers used in the reply (2026-09-16, published product, 2001-2010 mean, area-weighted, all vegetated land)
- Mycorrhizal C (NPP_NACTIVE+NPP_PACTIVE): **3.45 Pg C/yr** = 9.6% of NPP before the acquisition cost (NPP+NPP_NUPTAKE+NPP_PUPTAKE = 36.1 Pg C/yr);
  12.3% of reported NPP (28.1); 4.1% of AVAILC (83.3 Pg C/yr = GPP 114.2 minus maintenance respiration).
- N-acquisition C 3.43 Pg C/yr: 75% mycorrhizal, 25% root (non-myc), ~0% fixation (Defect C), retranslocation 0.01.
  P-acquisition C 4.63 Pg C/yr: 19% mycorrhizal, 21% root, the rest retranslocation.
- COST_NACTIVE area means: boreal (>50N) 6.28 gN/gC, temperate (23-50, both hemispheres) 1.16, tropics (<23) 1.78.
- Mycorrhizal C by zone: boreal 4.0 gC/m2/yr (2.0% of pre-cost NPP), temperate 14.0 (5.8%), tropics 68.5 (12.6%).
- Per-group table: see reply_to_ashley.md / replot_data.json (`pct_gross`). Figure regenerated with pre-cost-NPP labels
  (`replot_from_json.py`; the earlier version with %-of-reported-NPP labels kept as *_v1_pctNPPlabels.png).
- Layer file for Ashley: `ELM_FUNP_2022_mycorrhizal_C_layers_2001-2010.nc` (provisional; caveats in attributes).
- Corrected rerun (control vs A+B+C bundled) in progress: github.com/braghiere/ELM-FUN-2022-corrigendum; AM/EcM diagnostics
  wired in both transients, so the corrected layers will carry the AM/EcM split (per-PFT constant assignment).
