# pythran export rk2_step0(complex128[][][], complex128[][][], complex128[][][], float64[][], float)


def rk2_step0(state_spect_n12, state_spect, tendencies_n, diss2, dt):

    # transonic block (
    #     complex128[][][] state_spect_n12, state_spect,
    #                      tendencies_n;
    #     float64[][] diss2;
    #     float dt
    # )
    state_spect_n12[:] = (state_spect + ((dt / 2) * tendencies_n)) * diss2


# pythran export arguments_blocks
arguments_blocks = {
    "rk2_step0": ["state_spect_n12", "state_spect", "tendencies_n", "diss2", "dt"]
}

# pythran export __transonic__
__transonic__ = ("0.2.1",)
