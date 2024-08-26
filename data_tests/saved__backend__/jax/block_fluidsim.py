# __protected__ from jax import jit
# __protected__ @jit


def rk2_step0(state_spect_n12, state_spect, tendencies_n, diss2, dt):
    # transonic block (
    #     complex128[][][] state_spect_n12, state_spect,
    #                      tendencies_n;
    #     float64[][] diss2;
    #     float dt
    # )
    state_spect_n12[:] = (state_spect + dt / 2 * tendencies_n) * diss2


def arguments_blocks():
    return {
        "rk2_step0": [
            "state_spect_n12",
            "state_spect",
            "tendencies_n",
            "diss2",
            "dt",
        ]
    }


def __transonic__():
    return "0.7.1"
