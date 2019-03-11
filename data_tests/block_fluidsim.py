from transonic import Transonic

ts = Transonic()


class MyClass:
    def _time_step_RK2(self):
        dt = self.deltat
        diss, diss2 = self.exact_linear_coefs.get_updated_coefs()

        compute_tendencies = self.sim.tendencies_nonlin
        state_spect = self.sim.state.state_spect

        tendencies_n = compute_tendencies()

        state_spect_n12 = self._state_spect_tmp

        if ts.is_transpiled:
            ts.use_block("rk2_step0")
        else:
            # transonic block (
            #     complex128[][][] state_spect_n12, state_spect,
            #                      tendencies_n;
            #     float64[][] diss2;
            #     float dt
            # )
            state_spect_n12[:] = (state_spect + dt / 2 * tendencies_n) * diss2

        print("hello!")
