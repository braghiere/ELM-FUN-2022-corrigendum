# Re-plot of Ashley's ELM-FUN comparison with the correct variable (2026-09-16)

**What she plotted (panel A):** `COST_NACTIVE + COST_PACTIVE` from the FUN-P extracts. In the code these are
`cost_nactive = Nactive/npp_Nactive` (gN/gC) and `cost_pactive = Pactive/npp_Pactive` (gP/gC) — uptake
*efficiencies*, not carbon fluxes. Their sum has mixed units and is not "C allocation"; the y-axis label
"gC/m2/yr" on her figures is therefore incorrect. The apparent boreal 1:1 "match" is a numerical coincidence.

**Correct variable (panel B):** `NPP_NACTIVE + NPP_PACTIVE` (gC/m2/s -> gC/m2/yr): carbon actually spent on
mycorrhizal (AM+EcM) N and P uptake; excludes non-mycorrhizal uptake. Fraction of NPP = that / `NPP`
(ELM NPP = GPP - AR; FUN's uptake C is routed to soil, so it sits inside NPP). Do NOT use
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
  PFT 7 (temperate broadleaf deciduous) in the C4-grass/corn active-cost tier. Both bias mycorrhizal
  allocation; treat published ELM values as a modest LOWER bound, and treat the PFT-7 group as least reliable.
- Boreal soil mineral N over-accumulates in ELM (known), which cheapens N uptake and likely depresses boreal
  mycorrhizal allocation (2.1% of NPP).
- AM natural grasses come out very high (~108 gC/m2/yr, ~34% of NPP) — flag, not yet explained.
- Single deterministic run; no uncertainty layers exist.

Files: replot_hyphal_vs_ELM_corrected.png, replot_data.json (her x reads + ELM per-group stats).
