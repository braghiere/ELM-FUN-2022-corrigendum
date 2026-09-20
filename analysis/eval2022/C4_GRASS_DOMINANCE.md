# Why C4 grasses dominate the FUN carbon cost, and what "burned-off carbon" is

Question (2026-09-19): in the 1994-2005 evaluation, C4 grass (PFT 14) carries 66 % of the global carbon spent on N acquisition
(2.02 of 3.05 Pg C/yr in the control run; 83 % at the PFT level, `pft_table_1994-2005.md`) and pays 13-25 g C per g N against
0.3-4 g C per g N for every other PFT. Is that a parameter, a code tier, or the model's soil state?

## 1. Not the parameters, not a code tier

- The paramfile `clm_params_c200626.nc` carries x10 cost parameters for C4 grass (`akc_active` 0.6 vs 0.06, `kc_nonmyc` 7.2 vs 0.72,
  `kn_nonmyc` 0.12 vs 0.012 for all other PFTs). **They are never used**: the released `CNFUNMod.F90` overrides all of them with hard-coded
  tiers (lines 1389-1465, 1922-1970). The C4 tier (`ivt 14/17/18`) evaluates to exactly the default tier
  (`1.5/10 = 0.15`, `0.25/10 = 0.025`, `0.15*1 = 0.15`). The corrected code keeps the same tiers (only the `ivt 7 -> 17` typo changes).
- Defect B (`ivt.eq.7`) is in the AM tier and numerically inert (0.25/10 and 0.50/10 equal the default 0.025/0.050).

## 2. It is the soil state: C4 grasslands sit on the most N-poor soils in the model

Area-weighted means over cells where the PFT covers > 50 % (archived product, 1994-2005; `c4grass_diag.py`, `c4grass_diag.json`):

| dominant PFT | cells | N cost (g C m-2 yr-1) | N uptake (g N m-2 yr-1) | realized price (g C / g N) | soil mineral N (g N m-2) | fine-root C (g C m-2) | NPP after cost | net N mineralization (g N m-2 yr-1) |
|---|---|---|---|---|---|---|---|---|
| C4 grass | 120 | 249 | 9.9 | 25 | 1.9 (NO3 1.6, NH4 0.3) | 62 | 395 | 9.0 |
| C3 grass | 75 | 30 | 7.9 | 3.8 | 33 | 70 | 272 | 8.3 |
| C3 crop | 139 | 16 | 8.8 | 1.9 | 20 | 75 | 275 | 10.0 |
| tropical BDT | 74 | 26 | 7.3 | 3.6 | 15 | 54 | 242 | 8.8 |
| tropical BET | 254 | 10 | 18.5 | 0.5 | 3.0 | 209 | 820 | 23.5 |

The FUN cost of every soil pathway is `kn / N_available + kc / C_root` per layer. C4 cells have 2-3 x less mineral N per layer than
tropical forest and 8-17 x less than temperate grass and crops, and a third of the fine-root carbon of the forest, so every gram of N is
expensive; the plant still has the largest N demand per unit NPP of any group (35 g N m-2 yr-1 for 395 g C m-2 yr-1 of growth, the
default C4 leaf C:N of 25 and root C:N of 42) and meets only a quarter of it (uptake 9.9). The C4 cells are the Sahel and Sudanian
savannas (2.8 Mkm2), southern Africa and Madagascar (1.4), the cerrado and llanos (1.0) and northern Australia (0.6): seasonally dry
tropical grasslands with net N mineralization of 9 g N m-2 yr-1 (forest 23.5), no denitrification and almost no leaching in the model,
i.e. the soil N pool is small because the whole cycle turns over slowly at low litter N, and the FUN cost feeds back on it (expensive N
-> less NPP -> less litter -> less mineralization).

Why 25 g C per g N realized when the diagnosed AM price is 7? Part is averaging (the history variable `COST_NACTIVE` is a mean of a
rate, the realized price is a ratio of annual totals), the rest is the burned-off carbon below.

## 3. Burned-off carbon: the part of the cost that buys nothing

`NPP_NUPTAKE` and `NPP_PUPTAKE` (the carbon removed from growth and booked as respiration) are **not** the sum of the pathway costs.
In `CNFUNMod.F90` (released code, lines 2834-2878):

    soilc_change   = (npp_active + npp_nonmyc + npp_fix)/dt + npp_Nretrans + burned_off_carbon/dt
    soilc_change_p = (npp_active_pox + npp_nonmyc_pox + npp_retrans_p)/dt + burned_off_carbon_p/dt
    npp_Nuptake = soilc_change ; npp_Puptake = soilc_change_p

`burned_off_carbon` accumulates the `npp_to_spend` that is left when the algorithm has tried every soil layer and the pools it wanted to
draw from are empty (comment in the code: "burn off the extra carbon and hope this doesn't happen very often"). Global values,
1994-2005 (`burnedoff_by_group.json`):

| | archived v6 | control | corrected |
|---|---|---|---|
| N cost total / burned-off (Pg C/yr) | 3.77 / 0.00 | 3.05 / 0.22 | 2.92 / 0.21 |
| P cost total / burned-off (Pg C/yr) | 4.92 / 2.91 | 4.46 / 3.63 | 4.44 / 3.61 |
| burned-off share of the P cost | 59 % | 81 % | 81 % |
| share of P burned-off in C4-dominated cells | 32 % | 35 % | 35 % |

So the P "cost" that the paper reports as 1.6 Pg C/yr (its pathway sum) is 4.4-4.9 Pg C/yr in the model, and 60-80 % of it is carbon
spent without acquiring any phosphorus, in every biome (tropical deciduous trees 15 %, C3 grass, crops and temperate/boreal trees 10-12 %
each of the global burned-off). For N the burned-off term is small and lives almost entirely (85 %) in the C4 cells. Nutrient costs
remove 39-45 % of pre-cost NPP in C4-dominated cells, 24-28 % under tropical deciduous trees and 6-9 % under evergreen tropical and
temperate forests (`fig_c4grass_burnedoff_control_1994-2005.png`).

## 4. Consequences for the corrigendum

1. The C4 dominance is model behaviour of the released code on N-poor savanna soils, not a bug; it is the same in the archive,
   the control and the corrected run (C4 N cost 2.38 / 2.02 / 2.01 Pg C/yr). It should be stated when the global C-cost numbers are given.
2. The corrections do not touch it (C4 cost -0.5 %).
3. The paper's carbon-cost totals must be re-stated with the model's own accounting: N 3.05 (8.3 % of NPP) and P 4.46 Pg C/yr
   (12.2 %) in the released code, of which 3.6 Pg C/yr is burned-off carbon; or, if the pathway sums are kept (2.83 and 0.83 Pg C/yr),
   the text must say that the NPP reduction includes a further 3.8 Pg C/yr of carbon spent without return.
4. The 50 % NPP reduction of ELM-FUN3.0 relative to ELM is therefore only partly "the carbon cost of P": pre-cost NPP is 44 Pg C/yr
   against 71.5 for ELM, so most of the reduction (27 Pg C/yr) is growth downregulation by nutrient limitation and 7.5 Pg C/yr is the cost
   itself, half of which is burned-off.

Scripts: `c4grass_diag.py`, `fig_c4_burnedoff.py`; inputs `data/*_1994-2005_h0mean.nc`, `/home/braghiere/ELM_FUN_output/ELM_FUNP/ELM_FUNP.clm2.h0.185001-201012.nc`.
