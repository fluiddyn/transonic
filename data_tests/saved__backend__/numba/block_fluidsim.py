# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def rk2_step0(state_spect_n12, state_spect, tendencies_n, diss2, dt):
    # transonic block (
    #     complex128[][][] state_spect_n12, state_spect,
    #                      tendencies_n;
    #     float64[][] diss2;
    #     float dt
    # )
    state_spect_n12[:] = (state_spect + dt / 2 * tendencies_n) * diss2


# __protected__ @njit(cache=True, fastmath=True)


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


# __protected__ @njit(cache=True, fastmath=True)


def __transonic__():
    return "0.7.1"
