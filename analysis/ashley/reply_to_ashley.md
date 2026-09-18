Subject: Re: Global patterns in carbon allocation to mycorrhizal fungi

Hi Ashley,

Great to hear the paper is moving, and thanks for asking before comparing. You put your finger on exactly the right issue, and I went back into the model code and the 2022 output to give you a clear answer. Short version: the two models are not comparing the same thing yet, and the number you used is the reason. The fix is easy, and I have attached the layers you need.

What went wrong with the comparison. COST_NACTIVE and COST_PACTIVE are not amounts of carbon. They are exchange rates: how many grams of nitrogen (or phosphorus) a plant gets back for each gram of carbon it pays its fungi. Adding a nitrogen rate to a phosphorus rate does not give a physical quantity, and neither is carbon allocation. Your boreal points landing on the 1:1 line was a coincidence: in boreal soils the model's nitrogen rate happens to be about 5 grams of nitrogen per gram of carbon, close to your allocation numbers there, while elsewhere it is 1 to 2. Figure 2 shows this side by side with the corrected version.

What to use instead. The model does track the carbon plants actually spend on mycorrhizal uptake: NPP_NACTIVE (for nitrogen) plus NPP_PACTIVE (for phosphorus), in grams of carbon per square metre per second. That sum is the layer directly comparable to your hyphal allocation. It covers AM and EcM together, and it excludes uptake by roots alone, nitrogen fixation and nutrient recycling inside the plant.

One detail for turning it into a fraction of NPP. In this version of the model the carbon paid for nutrients is counted as respiration, so the NPP in the files is what is left after the plant has paid. To match the NPP you partition, add the payment back: NPP plus NPP_NUPTAKE plus NPP_PUPTAKE. I would not use the "available carbon" variable you saw in the supplement. That is photosynthesis minus maintenance respiration, a much larger pool (90 billion tonnes of carbon per year globally), so any fraction of it looks several times smaller than a fraction of NPP.

What the model says (Figure 1, 1994 to 2005 average, the period used in the paper). Globally, plants in ELM-FUN spend about 3.8 billion tonnes of carbon per year on mycorrhizal uptake, roughly 8 percent of NPP. The pattern is the reverse of what your first plot suggested: the model spends least in boreal forests (about 3 grams of carbon per square metre per year, 2 percent of NPP) and most in the tropics (about 65, or 11 percent). For your groups, the model sits well below your estimates for all forest types, by a factor of 3 to 9 for the EcM groups and about 2 for AM trees, and above your estimates for grasses and crops. The natural grass value in the model is oddly high (127 grams of carbon per square metre per year) and I would not read much into it. One practical note: please use 1994 to 2005 averages of that run. Its final year is not usable because the CO2 forcing file ended early, which is one of the things the rerun fixes.

Why the two differ. Your rates are fixed fractions from tracer studies. The model's plants shop for the cheapest nutrient source every hour, so they pay fungi little where soil nutrients are plentiful and more where they are scarce. That is a genuine reason to disagree, and an interesting one for the paper. The model also assumes one mycorrhizal type per plant type (conifers and boreal plants EcM, tropical trees, grasses and crops AM, temperate deciduous trees half and half) rather than a map, and the published files only contain the AM and EcM total, not the split.

One caveat. While digging into this we found three bugs in the 2022 code, including one that had effectively switched off symbiotic nitrogen fixation. We are rerunning the whole 1850 to 2010 simulation with the fixes and with the AM and EcM split switched on, and I should have the corrected layers within about a week. I do not expect the mycorrhizal numbers to move much: the forest gap comes from how cheaply the model's plants get nutrients, not from the bugs. The rerun mainly changes fixation. Everything is documented at github.com/braghiere/ELM-FUN-2022-corrigendum.

Uncertainty. There are no uncertainty layers, honestly. The published product is a single model run. The corrected and uncorrected pair will give you a rough bracket, and if it would help the paper I can add a small set of runs varying the mycorrhizal cost parameters.

Your timeline is fine for me, and a Zoom would be good. Thirty minutes should be enough to settle the exact layers.

Cheers,
Renato

Attachments:
- Figure 1: fig1_ELM_vs_thisstudy_by_group.png (carbon sent to mycorrhizal fungi, model versus your study, by group)
- Figure 2: replot_hyphal_vs_ELM_corrected.png (left, the comparison as first plotted; right, the corrected variable)
- ELM_FUNP_2022_mycorrhizal_C_layers_1994-2005.nc (1994 to 2005 mean maps: mycorrhizal carbon, NPP before the nutrient cost, their ratio, the two exchange rates; caveats in the file attributes)
