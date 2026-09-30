# A neuron on your screen

Live, interactive simulations of how brain cells fire, from a single neuron up to a network of a thousand. Everything runs in the browser, straight from the equations.

**[Try it live →](https://sukiraharris.github.io/Neuron-Simulator/)**

![Screenshot of the simulator](screenshot.png)

## What's inside

**One neuron, the Hodgkin–Huxley way.** A full implementation of the 1952 Hodgkin–Huxley model, the Nobel Prize-winning description of how sodium and potassium currents produce an action potential. You can adjust the input current and the sodium and potassium conductances, and watch the membrane voltage and the three gating variables (m, h, n) in real time.

**Different cells, different rhythms.** The Izhikevich (2003) model reproduces the firing patterns of real cortical neurons with only two equations and four parameters. Switch between regular spiking, intrinsically bursting, chattering, and fast-spiking cells to see how each responds when current turns on.

**A thousand neurons talking.** A network of 800 excitatory and 200 inhibitory Izhikevich neurons with random all-to-all connections and noisy background input. The raster plot shows every spike, and the population trace below it shows the network's collective rhythm. Changing connection strength moves the network between synchronized alpha/gamma-like oscillations and unstructured firing.

## How it works

- Hodgkin–Huxley equations integrated with forward Euler at 0.01 ms steps, using the classic squid giant axon parameters.
- Izhikevich neurons integrated at 0.25 ms (single cell) and 1 ms with two half-steps for membrane voltage (network), following Izhikevich (2003).
- Network connectivity stored as a flat 1000 × 1000 `Float32Array` in column-major order, so each spike adds one contiguous column to the input vector.
- Simulations pause automatically when scrolled off-screen, and start paused if the viewer prefers reduced motion.
- Plain HTML, CSS, and JavaScript with canvas rendering. No libraries or build step.

## Run it locally

Open `index.html` in any browser.

## References

- Hodgkin, A. L., & Huxley, A. F. (1952). A quantitative description of membrane current and its application to conduction and excitation in nerve. *The Journal of Physiology*, 117(4), 500–544.
- Izhikevich, E. M. (2003). Simple model of spiking neurons. *IEEE Transactions on Neural Networks*, 14(6), 1569–1572.

---

Built by [Sukira Harris](https://sukiraharris.github.io/Personal-Website/).
