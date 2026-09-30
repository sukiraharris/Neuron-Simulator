import json
import numpy as np
import matplotlib.pyplot as plt
from allensdk.core.cell_types_cache import CellTypesCache

ctc = CellTypesCache(manifest_file="cell_types/manifest.json")
cell_id = 489753277
data = ctc.get_ephys_data(cell_id)
sweeps = [s for s in ctc.get_ephys_sweeps(cell_id) if s["stimulus_name"] == "Long Square"]

rows = []
for s in sweeps:
    n = s["sweep_number"]
    spikes = data.get_spike_times(n)          # spike times in seconds
    isis = np.diff(spikes) * 1000             # gaps between spikes, in ms
    sw = data.get_sweep(n)
    v = sw["response"] * 1e3
    sr = sw["sampling_rate"]
    troughs = [v[int(t0 * sr):int(t1 * sr)].min() for t0, t1 in zip(spikes[:-1], spikes[1:])]
    stim = sw["stimulus"] * 1e12
    step_on = np.where(stim > 0.5 * s["stimulus_absolute_amplitude"])[0]
    latency = (spikes[0] - step_on[0] / sr) * 1000 if len(spikes) and len(step_on) else None
    rows.append({
        "sweep": n,
        "current_pA": round(s["stimulus_absolute_amplitude"], 1),
        "rate_hz": len(spikes) / 1.0,          # the step lasts 1 second
        "first_isi_ms": float(isis[0]) if len(isis) else None,
        "last_isi_ms": float(isis[-1]) if len(isis) else None,
        "isi_cv": float(np.std(isis) / np.mean(isis)) if len(isis) >= 2 else None,
        "trough_mv": float(np.mean(troughs)) if troughs else None,
        "latency_ms": float(latency) if latency is not None else None,
    })
    print(rows[-1])

rows.sort(key=lambda r: r["current_pA"])
json.dump({"cell_id": cell_id, "sweeps": rows}, open("fitting/target.json", "w"), indent=2)

plt.plot([r["current_pA"] for r in rows], [r["rate_hz"] for r in rows], "o-")
plt.xlabel("Injected current (pA)")
plt.ylabel("Firing rate (spikes/s)")
plt.title(f"F–I curve, cell {cell_id}")
plt.show()