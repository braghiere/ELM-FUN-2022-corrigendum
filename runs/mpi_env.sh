# MPI transport for ELM on CADES or-condo (2026-09-16 diagnosis, docs/PLAN.md):
# the openmpi/4.1.6 module has no InfiniBand BTL (tcp/vader/self only); its pml_ucx links spack UCX 1.16 which
# has rc_verbs/ud_verbs on mlx4_0. Force the UCX PML so inter-node traffic uses InfiniBand, never btl/tcp.
export OMPI_MCA_pml=ucx
export OMPI_MCA_osc=ucx
export OMPI_MCA_btl=^tcp,openib
export UCX_TLS=${UCX_TLS:-^ud}          # keep the ported machine-config choice (exclude ud transports)
export OMPI_MCA_pml_ucx_verbose=${OMPI_MCA_pml_ucx_verbose:-0}
