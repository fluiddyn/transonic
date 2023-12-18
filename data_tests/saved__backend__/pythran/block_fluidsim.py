def rk2_step0(state_spect_n12, state_spect, tendencies_n, diss2, dt):
    # transonic block (
    #     complex128[][][] state_spect_n12, state_spect,
    #                      tendencies_n;
    #     float64[][] diss2;
    #     float dt
    # )
    state_spect_n12[:] = (state_spect + ((dt / 2) * tendencies_n)) * diss2


arguments_blocks = {
    "rk2_step0": ["state_spect_n12", "state_spect", "tendencies_n", "diss2", "dt"]
}

__transonic__ = ("0.3.0",)
