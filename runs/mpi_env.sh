# MPI transport for ELM on CADES or-condo (diagnosed 2026-09-16, docs/PLAN.md):
# openmpi/4.1.6 has no InfiniBand BTL; its pml_ucx links spack UCX 1.16. On or-condo nodes mlx4_0 PORT 2 is a 10 GbE
# port (Link layer Ethernet) and PORT 1 is the 56 Gb InfiniBand link. Left to itself UCX picked rc_verbs on port 2
# (RoCE over lossy Ethernet) + tcp/ib0 and every rank spent ~1 s/step in MPI_Waitall in the coupler rearranger
# (8 sim-yr/day). Pin UCX to the InfiniBand port and force the UCX PML.
export OMPI_MCA_pml=ucx
export OMPI_MCA_osc=ucx
export OMPI_MCA_btl=^tcp,openib
export UCX_NET_DEVICES=mlx4_0:1
export UCX_TLS=rc_verbs,ud_verbs,sm,self
