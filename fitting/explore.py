import numpy as np
import matplotlib.pyplot as plt
from allensdk.core.cell_types_cache import CellTypesCache

ctc = CellTypesCache(manifest_file="cell_types/manifest.json")

# Pick a mouse cell
cell_id = 489753277
print("Cell:", cell_id)

# Find the "Long Square" sweeps: 1-second current steps
sweeps = ctc.get_ephys_sweeps(cell_id)
long_sq = [s for s in sweeps if s["stimulus_name"] == "Long Square"]
for s in long_sq:
    print(s["sweep_number"], s["stimulus_absolute_amplitude"], "pA")

# Load the recording and plot several sweeps
data = ctc.get_ephys_data(cell_id)
picks = long_sq[::max(1, len(long_sq) // 5)]   # about 5 sweeps, low to high current

fig, axes = plt.subplots(len(picks), 1, sharex=True, figsize=(10, 2 * len(picks)))
for ax, s in zip(axes, picks):
    sw = data.get_sweep(s["sweep_number"])
    start, end = sw["index_range"]
    t = np.arange(end - start) / sw["sampling_rate"]
    v = sw["response"][start:end] * 1e3
    ax.plot(t, v, lw=0.8)
    ax.set_ylabel(f'{s["stimulus_absolute_amplitude"]:.0f} pA')
axes[-1].set_xlabel("s")
plt.tight_layout()
plt.show()