import json
import numpy as np
import matplotlib.pyplot as plt
from numba import njit
from scipy.optimize import differential_evolution
from allensdk.core.cell_types_cache import CellTypesCache

VR, VPEAK = -70.0, 35.0   # resting voltage (from the data) and spike peak, kept fixed
HOLDOUT = 110.0           # current hidden from the optimizer, used to test the fit

@njit
def run(C, k, vt, a, b, c, d, I, T, dt):
    """Izhikevich (2007) neuron. Returns spike times (ms) and the lowest voltage before each spike."""
    v, u = VR, 0.0
    spikes = np.empty(1000)
    troughs = np.empty(1000)
    n = 0
    vmin = 1e9
    for step in range(int(T / dt)):
        v += dt * (k * (v - VR) * (v - vt) - u + I) / C
        u += dt * a * (b * (v - VR) - u)
        if v != v:
            break
        if v < vmin:
            vmin = v
        if v >= VPEAK:
            v = c
            u += d
            if n < 1000:
                spikes[n] = step * dt
                troughs[n] = vmin
                n += 1
            vmin = 1e9
    return spikes[:n], troughs[:n]

@njit
def trace(C, k, vt, a, b, c, d, I, T, dt):
    """Same model, but returns the voltage trace for plotting."""
    steps = int(T / dt)
    out = np.empty(steps)
    v, u = VR, 0.0
    for step in range(steps):
        v += dt * (k * (v - VR) * (v - vt) - u + I) / C
        u += dt * a * (b * (v - VR) - u)
        if v >= VPEAK:
            out[step] = VPEAK
            v = c
            u += d
        else:
            out[step] = v
    return out

target = json.load(open("fitting/target.json"))
sweeps = [s for s in target["sweeps"] if s["current_pA"] >= 0]
train = [s for s in sweeps if s["current_pA"] != HOLDOUT]

def loss(x):
    err = 0.0
    for s in train:
        sp, tr = run(*x, s["current_pA"], 1000.0, 0.1)
        err += (len(sp) - s["rate_hz"]) ** 2                      # firing rate
        if s["first_isi_ms"] and len(sp) >= 2:                     # adaptation
            isi = np.diff(sp)
            err += 25 * ((isi[0] - s["first_isi_ms"]) / s["first_isi_ms"]) ** 2
            err += 25 * ((isi[-1] - s["last_isi_ms"]) / s["last_isi_ms"]) ** 2
        if s.get("isi_cv") is not None and len(sp) >= 3:           # regularity
            isi = np.diff(sp)
            err += 200 * (np.std(isi) / np.mean(isi) - s["isi_cv"]) ** 2
        if s.get("trough_mv") is not None and len(sp) >= 3:          # spike shape
            err += 0.5 * (np.mean(tr[1:]) - s["trough_mv"]) ** 2
    return err / len(train)

#          C          k          vt           a             b          c           d
bounds = [(50, 300), (0.1, 3), (-60, -30), (0.001, 0.2), (-10, 10), (-65, -35), (0, 300)]

if __name__ == "__main__":
    result = differential_evolution(loss, bounds, maxiter=80, popsize=20,
                                    seed=0, polish=False, disp=True)
    names = ["C", "k", "vt", "a", "b", "c", "d"]
    fit = dict(zip(names, map(float, result.x)))
    fit.update(vr=VR, vpeak=VPEAK, loss=float(result.fun))
    print("\nFitted parameters:", json.dumps(fit, indent=2))
    json.dump(fit, open("fitting/fit.json", "w"), indent=2)

    # How well does it do, including on the held-out current?
    for s in sweeps:
        model = len(run(*result.x, s["current_pA"], 1000.0, 0.1)[0])
        tag = "  <- held out" if s["current_pA"] == HOLDOUT else ""
        print(f'{s["current_pA"]:6.0f} pA   real {s["rate_hz"]:4.0f}   model {model:4d}{tag}')

    # Plot 1: F-I curves
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    cur = [s["current_pA"] for s in sweeps]
    ax1.plot(cur, [s["rate_hz"] for s in sweeps], "o", label="Real neuron")
    ax1.plot(cur, [len(run(*result.x, I, 1000.0, 0.1)[0]) for I in cur], "s-", label="Fitted model")
    ax1.axvline(HOLDOUT, ls="--", c="grey", label="Held-out current")
    ax1.set_xlabel("Injected current (pA)"); ax1.set_ylabel("Firing rate (spikes/s)"); ax1.legend()

    # Plot 2: real vs model voltage at 130 pA
    ctc = CellTypesCache(manifest_file="cell_types/manifest.json")
    data = ctc.get_ephys_data(target["cell_id"])
    s130 = min(sweeps, key=lambda s: abs(s["current_pA"] - 130))
    sw = data.get_sweep(s130["sweep"])
    rate = sw["sampling_rate"]
    i_real = sw["stimulus"] * 1e12
    onset = np.where(i_real > 0.5 * s130["current_pA"])[0][0]
    seg = slice(onset, onset + int(1.0 * rate))
    t_real = np.arange(seg.stop - seg.start) / rate * 1000
    ax2.plot(t_real, sw["response"][seg] * 1e3, lw=0.8, label="Real neuron")
    ax2.plot(np.arange(10000) * 0.1, trace(*result.x, s130["current_pA"], 1000.0, 0.1),
             lw=0.8, alpha=0.8, label="Fitted model")
    ax2.set_xlabel("Time from current onset (ms)"); ax2.set_ylabel("mV")
    ax2.set_title(f'{s130["current_pA"]:.0f} pA'); ax2.legend()
    plt.tight_layout(); plt.show()