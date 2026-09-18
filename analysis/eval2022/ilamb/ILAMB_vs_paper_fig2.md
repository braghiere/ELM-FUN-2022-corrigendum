# ILAMB overall scores: archived products (ILAMB 2.7, current datasets, 1994–2005) vs the paper's Figure 2 (ILAMB 2.6, 2022)
First run (`_build_published`, before the soil-C/ET fixes and before trimming the CO₂-collapse years):

| benchmark | ELM (paper) | ELM-FUN2.0 (paper) | ELM-FUN3.0 (paper) | note |
|---|---|---|---|---|
| Biomass | 0.59 (0.44) | 0.64 (0.54) | 0.70 (0.72) | current ILAMB uses Saatchi2011 + GEOCARBON; the paper's "GlobalCarbon" set is no longer distributed |
| Gross primary productivity (FLUXCOM) | 0.65 (0.66) | 0.66 (0.67) | 0.67 (0.68) | |
| Leaf area index (MODIS) | 0.43 (0.39) | 0.48 (0.44) | 0.54 (0.51) | |
| Global net ecosystem carbon balance | 0.09 (0.61) | 0.13 (0.59) | 0.15 (0.58) | the NBP benchmark spans 1959–2010 and includes the collapsed 2009–2010; rerun with products trimmed to 2008 |
| Net ecosystem exchange (FLUXNET2015) | 0.41 (0.39) | 0.42 (0.41) | 0.43 (0.41) | |
| Ecosystem respiration (FLUXCOM) | 0.49 (0.49) | 0.49 (0.50) | 0.56 (0.57) | |
| Soil carbon (HWSD) | – (0.55) | – (0.59) | – (0.68) | failed: benchmark variable is `cSoilAbove1m`; fixed in cfg, rerun |
| Evapotranspiration (GLEAM) | – (0.50) | – (0.51) | – (0.54) | failed: 2022 CMOR set has only `evspsblsoi/evspsblveg/tran`; derived sum added, rerun |

GPP, LAI, NEE and respiration reproduce the paper's scores and ordering (FUN3.0 best) within ~0.04. Biomass keeps the ordering with a
different dataset. The NBP score collapses because of the CO₂-forcing failure at the end of the archived runs.

## Second run (`_build_published3`): soil-C/ET fixed, archived products trimmed to 2008 (`scores_published_trimmed2008.csv`)
| benchmark | ELM (paper) | ELM-FUN2.0 (paper) | ELM-FUN3.0 (paper) |
|---|---|---|---|
| Soil carbon (HWSD) | 0.55 (0.55) | 0.58 (0.59) | 0.68 (0.68) |
| Evapotranspiration (GLEAM v3.3a) | 0.72 (0.50) | 0.72 (0.51) | 0.71 (0.54) |
| Global net ecosystem carbon balance | 0.09 (0.61) | 0.13 (0.59) | 0.15 (0.58) |
Soil carbon reproduces the paper to two decimals. Evapotranspiration differs (different GLEAM release / ILAMB scoring). The NBP
score stays near 0.1 even without the 2009–2010 collapse: the archived `nbp` diagnostic is a 20–37 Pg C/yr source (see the
budget-closure item), which no benchmark accepts; the paper's 0.6 therefore came from a different nbp than the archived one.
