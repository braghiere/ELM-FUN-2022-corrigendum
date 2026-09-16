"""Wire AM/EcM C-flux diagnostics (npp_Nam/Necm/Pam/Pecm) in CNFUNMod.F90. Pattern-anchored. DRY RUN unless --apply.
Uses per-step accumulators incl. the retrans step so EcM+AM == Nactive exactly (istp==ecm_step -> EcM)."""
import sys,re,shutil
src=sys.argv[1]; apply='--apply' in sys.argv; t=open(src).read()
nA=re.search(r'^(\s*)npp_Nactive\(p\)\s*=\s*npp_Nactive_no3\(p\)\s*\+\s*npp_Nactive_nh4\(p\).*$',t,re.M)
pA=re.search(r'^(\s*)npp_Pactive\(p\)\s*=\s*npp_Pactive\(p\).*$',t,re.M); assert nA and pA,"anchors missing"
i,j=nA.group(1),pA.group(1)
nI=(f"\n{i}! --- AM/EcM split of mycorrhizal N-uptake C (diagnostic only, exact closure; wired 2026-09) ---\n"
    f"{i}npp_Necm(p) = ( npp_active_no3_acc(p,ecm_step) + npp_active_nh4_acc(p,ecm_step) &\n"
    f"{i}              + npp_active_no3_retrans(p,ecm_step) + npp_active_nh4_retrans(p,ecm_step) )/dt\n"
    f"{i}npp_Nam(p)  = npp_Nactive(p) - npp_Necm(p)")
pI=(f"\n{j}! --- AM/EcM split of mycorrhizal P-uptake C (diagnostic only, exact closure; wired 2026-09) ---\n"
    f"{j}npp_Pecm(p) = ( npp_active_pox_acc(p,ecm_step) + npp_active_pox_retrans(p,ecm_step) )/dt\n"
    f"{j}npp_Pam(p)  = npp_Pactive(p) - npp_Pecm(p)")
out=t[:nA.end()]+nI+t[nA.end():]; m=re.search(r'^(\s*)npp_Pactive\(p\)\s*=\s*npp_Pactive\(p\).*$',out,re.M); out=out[:m.end()]+pI+out[m.end():]
need=('ecm_step','npp_active_no3_acc(p,istp)','npp_active_no3_retrans(p,istp)','npp_active_pox_retrans(p,istp)','npp_Necm','npp_Pam')
print(("APPLYING" if apply else "DRY RUN"),"->",src); print("  anchors at lines",t[:nA.start()].count('\n')+1,"/",t[:pA.start()].count('\n')+1,"| all symbols present:",all(s in t for s in need))
if apply: shutil.copy(src,src+'.pre_amecm_bak'); open(src,'w').write(out); print("  applied; backup",src+'.pre_amecm_bak')
