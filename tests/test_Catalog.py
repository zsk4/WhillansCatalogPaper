import src.Catalog.Catalog as Catalog
import os
import pandas as pd


def test_init():
    # Example directory set up to contain full, partial, and empty .pos files
    dir = "./tests"
    sta = "ExamplePos"
    years = ["2010", "2011"]
    interpolation_time = 15

    cat = Catalog.Datastream(os.path.join(dir, sta), sta, years, interpolation_time)
    # Check metadata
    assert cat.sta == os.path.join(dir, sta)
    assert cat.name == sta
    assert cat.years == years
    assert cat.interpolation_time == interpolation_time

    # Check data frame
    assert cat.data["x"].iloc[0] == -283558.7202622765
    assert cat.data["x"].iloc[-1] == -283555.9024088845
    assert cat.data["y"].iloc[0] == -560187.0467522554
    assert cat.data["y"].iloc[-1] == -560188.350685506

    assert cat.data["time"].iloc[-1] == pd.Timestamp("2011-01-01 23:59:45")
    assert cat.data["time"].iloc[-2] == pd.Timestamp("2011-01-01 23:54:15")
