import os

import src.Catalog.Catalog as Catalog

stas = ["la01", "la02", "la05"]
years = ["2010", "2011"]
max_gap_len = 120
dir = "./tests/ExamplePos"

cats = []
for sta in stas:
    interpolation_time, run = Catalog.set_interpolation_time(sta, years)
    cat = Catalog.Datastream(os.path.join(dir, sta), sta, years, interpolation_time)
    cat.findgaps(max_gap_len)
    cats.append(cat)
picks = Catalog.Picks(cats)

picks.lls_detection(600, 20)
merged_df = picks.merge()
sorted_list = picks.on_off_list()
# print(sorted_list)
picks.no_data_csv(sorted_list)

merged = Catalog.Events(merged_df)
threshold = merged.pick_events(sorted_list, active_stas=2)
indices = merged.on_off_indices(sorted_list)
# merged.plot_picking(indices, threshold, num_plots=25)
catalog = merged.make_catalog(cull_time=30, cull_dist=0.1)
# print(catalog)
# for event in catalog[:25]:
#    Catalog.plot_event(event)
