import pandas as pd
from allensdk.core.cell_types_cache import CellTypesCache

ctc = CellTypesCache(manifest_file="cell_types/manifest.json")

cells = pd.DataFrame(ctc.get_cells(species=["Mus musculus"]))
feats = pd.DataFrame(ctc.get_ephys_features())
df = cells.merge(feats, left_on="id", right_on="specimen_id")

# Spiny = excitatory pyramidal cells. Keep ones that fire steadily.
spiny = df[(df["dendrite_type"] == "spiny") & (df["f_i_curve_slope"] > 0.1)]
cols = ["specimen_id", "f_i_curve_slope", "avg_isi", "adaptation", "vrest"]
print(spiny[cols].sort_values("f_i_curve_slope", ascending=False).head(10).to_string())