import json
import numpy as np
import matplotlib.pyplot as plt

def simulate(p, I, T=1000.0, dt=0.1):
    """Izhikevich (2007) neuron. Returns spike times (ms) for a constant current I (pA)."""
    C, k, vr, vt, a, b, c, d, vpeak = p
    v, u = vr, 0.0
    spikes = []
    for step in range(int(T / dt)):
        v += dt * (k * (v - vr) * (v - vt) - u + I) / C
        u += dt * a * (b * (v - vr) - u)
        if v >= vpeak:
            v = c
            u += d
            spikes.append(step * dt)
    return np.array(spikes)

# Izhikevich's textbook regular-spiking pyramidal cell, with rest set to this cell's -70 mV
p_default = [100, 0.7, -70, -50, 0.03, -2, -50, 100, 35]

target = json.load(open("fitting/target.json"))
currents = [s["current_pA"] for s in target["sweeps"]]
real_rates = [s["rate_hz"] for s in target["sweeps"]]
model_rates = [len(simulate(p_default, I)) for I in currents]

plt.plot(currents, real_rates, "o", label="Real neuron")
plt.plot(currents, model_rates, "s-", label="Model (textbook settings)")
plt.xlabel("Injected current (pA)")
plt.ylabel("Firing rate (spikes/s)")
plt.legend()
plt.show()