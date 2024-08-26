import src.Catalog.Catalog as Catalog
import src.Catalog.CatalogWrapper as CatWrap
import os
import pandas as pd


def test_wrapper():
    dir = "./tests/ExamplePos"
    stas = ["la01", "la05"]
    years = ["2010", "2011"]
    interpolation_time = 15
    max_gap_len = 120

    cats = []
    for sta in stas:
        cat = Catalog.Datastream(os.path.join(dir, sta), sta, years, interpolation_time)
        cat.findgaps(max_gap_len)
        cats.append(cat)

    # Without plotting
    catalog = CatWrap.full_catalog_run(
        cats,
        years,
        window=600,
        slide=25,
        active_stas=2,
        cull_time=30,
        cull_dist=0.1,
        plot=False,
    )

    assert len(catalog) == 5
    assert catalog[0]["time"].iloc[0] == pd.Timestamp("2010-12-30 09:35:00")
    assert catalog[0]["time"].iloc[-1] == pd.Timestamp("2010-12-30 13:44:45")

    # With plotting
    catalog = CatWrap.full_catalog_run(
        cats,
        years,
        window=600,
        slide=25,
        active_stas=2,
        cull_time=30,
        cull_dist=0.1,
        plot=True,
    )

    assert len(catalog) == 5
    assert catalog[0]["time"].iloc[0] == pd.Timestamp("2010-12-30 09:35:00")
    assert catalog[0]["time"].iloc[-1] == pd.Timestamp("2010-12-30 13:44:45")
