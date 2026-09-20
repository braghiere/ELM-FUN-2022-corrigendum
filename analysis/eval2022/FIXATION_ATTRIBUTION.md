# Why symbiotic N fixation was ~0 in the 2022 runs: attribution to the three code defects

Question (2026-09-20): was the missing symbiotic fixation caused by the hard-coded fixation cost (defect C), by the larch kc/kn swap
(defect A), by the `ivt 7 -> 17` tier typo (defect B), or a combination?

**Answer: defect C alone.** A and B cannot reach the fixation pathway, and the signature of C is visible in every PFT.

## 1. The released code differs from the corrected code in exactly three places
`diff runs/srcmods_ctl/src.clm/CNFUNMod.F90 runs/srcmods_fixABC/src.clm/CNFUNMod.F90` (comments excluded):
1. `ivt(p).eq.7` -> `ivt(p).eq.17` in the AM active-uptake tier (B). The tier values 0.25/10 and 0.50/10 equal the default 0.025/0.050,
   so the branch is numerically inert for PFT 7 and for PFT 17 alike.
2. larch (PFT 3) direct-root parameters `kc_nonmyc = 0.15, kn_nonmyc = 0.015` -> `0.015, 0.15` (A). Touches one pathway of one PFT
   (1.5 Mkm2, boreal needleleaf deciduous); larch fixes nothing in either run.
3. the fixation cost (C), function `fun_cost_fix`, line 3010 of the released module:

       released:  fun_cost_fix = 30 / (1.25 * exp(-3.62 - 0.27*T*(1 - 0.5*T/25.14)))
       corrected: fun_cost_fix = s_fix * (exp(a_fix + b_fix*T*(1 - 0.5*T/25.14)) - 2)      ! s_fix = -6, a = -3.62, b = 0.27 (paramfile)

   The released line is an experimental variant left active (the intermediate form is still in a comment on line 3008): s_fix
   replaced by -30, the multiplication turned into a division, the sign of the temperature coefficient flipped and the "- 2" dropped.

## 2. Size and shape of the two cost functions (g C per g N)
| soil T (C) | released hard-coded | paramfile form (Fisher et al. 2010 / Houlton et al. 2008, s_fix = -6) |
|---|---|---|
| 0 | 896 | 11.8 |
| 10 | 7,794 | 10.6 |
| 20 | 23,158 | 7.8 |
| 25 | 26,685 | 7.2 |
| 30 | 23,509 | 7.8 |

The released cost is 100-3,000 times the intended one and inverted with temperature: fixation is most expensive at 25 C, where
Houlton's response says it should be cheapest. Against mycorrhizal and root prices of 0.3-20 g C per g N, fixation never wins.

## 3. The signature is in every PFT, including the 13 that A and B do not touch
Symbiotic fixation 1994-2005, direct integration of the PFT history stream (`pfts1d_wtgcell x area x landfrac`; the gridded stream gives
the same totals, 3.135 vs 3.134 Tg N/yr):

| PFT | control (released code) | corrected | touched by A or B? |
|---|---|---|---|
| all PFTs together | 0.0001 Tg N/yr, realized cost 4,082 g C per g N | 3.13 Tg N/yr, realized cost 7.96 g C per g N | |
| tropical BET (4) | 0 | 0.66 | no |
| C3 grass (13) | 0 | 1.37 | no |
| temperate BDS (10) | 0 | 0.26 | no |
| C3 arctic grass (12) | 0 | 0.21 | no |
| temperate BDT (7) | 0 | 0.20 | B (inert) |
| tropical BDT (6) | 0 | 0.16 | no |
| larch (3) | 0 | 0 | A |
| C4 grass (14), crops (15, 16) | 0 | 0 | B (inert) / fracfixers = 0 |

In the control the realized cost by PFT is 1,900-58,000 g C per g N, i.e. the hard-coded range at boreal to tropical soil temperatures.
The corrected realized cost (7.96) is the paramfile form at 20-30 C, where most of the fixation happens.

## 4. Why fixation is still small after the fix
3.1 Tg N/yr against 52-130 in the Davies-Barnard & Friedlingstein (2020) compilation, because in ELM-FUN mycorrhizal and direct-root
uptake cost 0.3-3 g C per g N over most of the vegetated land (see `C4_GRASS_DOMINANCE.md`), so a 7-12 g C per g N fixer is rarely the
cheapest option; only in the N-poor tropics and in grasslands does it take 1-7 % of the N-acquisition carbon. That is a property of the
FUN cost parameters, not a defect.

A single-defect run (C alone) would make the attribution formal, but given that A reaches one pathway of one non-fixing PFT and B is
numerically inert, the bundled A+B+C run already isolates C for the fixation flux.
