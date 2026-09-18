# Sneak peek: control vs corrected (A+B+C) vs published, 1860–1879 means (runs in progress, 2026-09-18 14:30)
Both transients start from the identical 2020-tree FUN-off spin-up restart (r.0541), so control→corrected isolates the three fixes.
Published = fix_global_v6_funp (2022 product), same years. Area-weighted global totals.

| variable | control | corrected | Δ corrected−control | published |
|---|---|---|---|---|
| GPP (Pg C/yr) | 96.31 | 96.64 | +0.3 % | 96.59 |
| NPP reported (Pg C/yr) | 26.31 | 26.51 | +0.7 % | 26.11 |
| HR (Pg C/yr) | 44.19 | 44.38 | +0.4 % | 43.98 |
| TOTVEGC (Pg C) | 553.1 | 554.0 | +0.2 % | 552.2 |
| TOTECOSYSC (Pg C) | 2684.7 | 2687.2 | +0.1 % | 2683.0 |
| SMINN (Pg N) | 1.164 | 1.163 | −0.1 % | 1.179 |
| **symbiotic N fixation NFIX (Tg N/yr)** | **0.00** | **4.31** | from ~0 | 0.00 |
| realized fixation cost ΣNPP_NFIX/ΣNFIX (gC/gN) | 5,586 | **7.8** | | 6,168 |
| free-living fixation (Tg N/yr) | 39.14 | 39.18 | +0.1 % | 39.18 |
| C spent on N acquisition NPP_NUPTAKE (Pg C/yr) | 4.95 | 4.84 | −2.2 % | 5.52 |
| mycorrhizal N-uptake C NPP_NACTIVE (Pg C/yr) | 3.38 | 3.28 | −3.0 % | 4.12 |
| root N-uptake C NPP_NNONMYC (Pg C/yr) | 1.10 | 1.07 | −2.8 % | 1.38 |
| EcM share of mycorrhizal C (new diagnostic) | 5 % | 5 % | NPP_NECM −13 % | not in product (0) |
| C spent on P acquisition NPP_PUPTAKE (Pg C/yr) | 4.96 | 4.94 | −0.5 % | 5.31 |
| mycorrhizal P-uptake C NPP_PACTIVE (Pg C/yr) | 0.39 | 0.39 | +0.3 % | 0.95 |

By zone (corrected vs control): symbiotic fixation boreal 0.12, temperate 1.47, tropics 2.72 Tg N/yr (all ~0 in control);
mycorrhizal C −3.9 % boreal, −9.2 % temperate, −1.7 % tropics; NPP and TOTVEGC within +1 %.

**Reading.** (1) The corrections change essentially one thing in the first three decades: symbiotic fixation switches on at a
physical cost (7.8 gC/gN) but stays small, 4.3 Tg N/yr, about a tenth of the model's free-living fixation and far below
literature values of tens of Tg N/yr for natural symbiotic BNF — ELM's mycorrhizal/root uptake at 0.2–0.9 gC/gN outcompetes
fixation almost everywhere. (2) Mycorrhizal carbon falls 3 % globally (9 % temperate), as predicted from the code (larch tier
swap + fixation displacing uptake); the PFT-7 fix is inert. (3) Carbon stocks and fluxes move by <1 %. (4) The control
reproduces the published carbon budget to within ~1 % (GPP, NPP, HR, stocks) and SMINN to 1 %; N-acquisition C is 10 % lower and
the P-acquisition partition differs (published spends 0.95 Pg C/yr on mycorrhizal P vs our 0.39, with more P retranslocation in
ours) — to be examined in the full analysis (candidate: spin-up P state / surface-dataset P fields). Early-period numbers; the
final report covers 1850–2010.
