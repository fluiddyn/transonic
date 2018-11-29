

from fluidpythran import FluidPythran

fp = FluidPythran()


class MyClass:
    def _time_step_RK2_fluidpythran(self):
        dt = self.deltat
        diss, diss2 = self.exact_linear_coefs.get_updated_coefs()

        compute_tendencies = self.sim.tendencies_nonlin
        state_spect = self.sim.state.state_spect

        tendencies_n = compute_tendencies()

        state_spect_n12 = self._state_spect_tmp

        if fp.is_transpiled:
            fp.use_pythranized_block("rk2_step0")
        else:
            # pythran block (
            #     complex128[][][] state_spect_n12, state_spect,
            #                      tendencies_n;
            #     float64[][] diss2;
            #     float dt
            # )
            state_spect_n12[:] = (state_spect + dt / 2 * tendencies_n) * diss2

        print("hello!")