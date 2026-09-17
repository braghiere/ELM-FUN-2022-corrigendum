Subject: Re: Global patterns in carbon allocation to mycorrhizal fungi

Hi Ashley,

Great to hear the paper is moving, and thank you for checking the variables before comparing. You asked exactly the right question. I went back into the code and the 2022 output, and the short answer is that the two models are not both apples yet, mostly because of the variable, but the fix is simple and I have put the comparable layers together for you (attached, with one important caveat at the end).

1. The variable. COST_NACTIVE and COST_PACTIVE are not carbon fluxes. In the code they are N acquired divided by C spent, and the same for P, so their units are gN per gC and gP per gC. They are uptake efficiencies, and their sum has mixed units. I think this is why your boreal points fell on the 1:1 line: COST_NACTIVE averages 6.3 gN per gC north of 50 N, 1.2 gN per gC in the temperate zone and 1.8 gN per gC in the tropics, so the boreal match is a coincidence between two unrelated quantities. The carbon actually spent on mycorrhizal uptake is NPP_NACTIVE plus NPP_PACTIVE (gC per m2 per s in the files). It covers AM and EcM together and excludes root uptake, fixation and retranslocation, so it is the right "allocation to mycorrhizae" layer.

2. The denominator. I would not use AVAILC. In ELM it is GPP minus maintenance respiration, 83 Pg C per yr globally in that run, so a fraction of it comes out several times smaller than a fraction of NPP. There is also a subtlety in the 2022 build: the carbon spent on N and P acquisition is booked into autotrophic respiration, so the NPP written to the files already has that cost removed. The quantity comparable to the NPP you partition is NPP plus NPP_NUPTAKE plus NPP_PUPTAKE, and the fraction you want is NPP_NACTIVE plus NPP_PACTIVE divided by that sum. Both layers are in the attached file.

3. What ELM-FUN gives (published run, 2001 to 2010 mean). Globally 3.5 Pg C per yr goes to mycorrhizal N and P uptake, 9.6 percent of NPP before the acquisition cost. Boreal (north of 50 N): 4 gC per m2 per yr, 2.0 percent. Temperate (23 to 50 degrees): 14 gC per m2 per yr, 5.8 percent. Tropics: 69 gC per m2 per yr, 12.6 percent. For your groups, using grid cells classified by dominant PFT and your group means as I read them off your figures:

Group | ELM mycorrhizal C, gC per m2 per yr (10th to 90th percentile) | ELM share of NPP | your estimate, gC per m2 per yr
AM crops | 15 (5 to 26) | 4.7 percent | 7
AM natural grasses | 108 (5 to 248) | 17.1 percent | 20
AM trees and shrubs | 33 (10 to 61) | 5.7 percent | 62
EcM broadleaf trees and shrubs | 5 (2 to 6) | 2.3 percent | 40
EcM needleleaf trees and shrubs | 6 (2 to 15) | 2.2 percent | 22
EcM deciduous needleleaf trees | 2 (1 to 2) | 0.9 percent | 15
EcM evergreen needleleaf trees | 7 (3 to 15) | 2.3 percent | 25

So with the right variable the picture flips: ELM allocates least in boreal forests and most in the tropics, your EcM estimates are 3 to 9 times higher than ELM's, and your AM tree estimate is about double. ELM's AM natural grasses are the odd group (108 gC per m2 per yr) and I would not lean on that one yet. The attached figure shows both versions of the comparison.

4. Why they are not both apples. Your rates are fixed empirical fractions of NPP. ELM's are the outcome of a cost minimisation that responds to plant demand and soil supply at every time step, so it spends less where nutrients are abundant and more where they are scarce. That is a real reason to diverge and a useful one to discuss. Two structural points as well. ELM assigns association type as a per PFT constant (0.99 EcM, 0.01 EcM, or 0.5 for temperate broadleaf deciduous), not a spatial MFT map, so it resolves far less of the variation your 19 PFT by MFT groups do. And the published output only has total mycorrhizal C: the separate AM and EcM diagnostics exist in the code but were never populated, so they are zero in the files.

5. The caveat. While looking into this we found three inherited defects in the 2022 FUN code: a swapped pair of root uptake cost parameters (the same problem later fixed in CTSM, issue 2120), a PFT index typo, and a hardcoded fixation cost of roughly 900 to 27,000 gC per gN that effectively switched symbiotic fixation off. A corrected rerun of the full 1850 to 2010 simulation is running now, with the AM and EcM diagnostics wired in, and I expect the corrected layers within about a week. For your comparison I do not expect them to move much: in this code version the swap only affects larch, the typo turns out to be numerically inert, and fixation at 7 to 12 gC per gN still loses to mycorrhizal uptake almost everywhere, so the gap you see for forests is a real feature of the model (cheap nutrient uptake under the cost optimisation), not a bug artifact. The rerun mainly changes fixation. I will send the corrected layers and the AM versus EcM split as soon as they are done, and everything is documented at github.com/braghiere/ELM-FUN-2022-corrigendum.

6. Uncertainty. There are no uncertainty layers: the published product is a single deterministic run. The control versus corrected pair I am running gives at least a structural bracket, and if it helps I can add a small parameter perturbation on the mycorrhizal cost parameters. One known behaviour to keep in mind: ELM over accumulates mineral N in cold soils, which makes boreal N cheap and depresses boreal mycorrhizal spending.

Your timeline is fine for me and a Zoom would be good. Thirty minutes should be enough to settle the exact layers.

Cheers,
Renato

Attachments:
- replot_hyphal_vs_ELM_corrected.png (panel A: what was plotted; panel B: the comparable carbon flux)
- ELM_FUNP_2022_mycorrhizal_C_layers_2001-2010.nc (2022 layers: mycorrhizal C, NPP before the acquisition cost, their ratio, AVAILC, COST_NACTIVE, COST_PACTIVE; caveats in the file attributes)
