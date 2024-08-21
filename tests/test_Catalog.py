import src.Catalog.Catalog as Catalog
import os
import pandas as pd
import pytest


def test_datastream_init():
    # Example directory set up to contain full, partial, and empty .pos files
    dir = "./tests/ExamplePos"
    sta = "la01"
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


def test_interpolation():
    # Example directory set up to contain full, partial, and empty .pos files
    dir = "./tests/ExamplePos"
    sta = "la01"
    years = ["2010", "2011"]
    interpolation_time = 15
    max_gap_len = 120

    # Check interpolation
    cat = Catalog.Datastream(os.path.join(dir, sta), sta, years, interpolation_time)
    int_cat = cat.findgaps(interpolation_time, max_gap_len)  # Interpolate Data
    assert int_cat.data["time"].iloc[-1] == pd.Timestamp("2011-01-01 23:59:45")
    assert int_cat.data["time"].iloc[-2] == pd.Timestamp("2011-01-01 23:54:15")
    assert int_cat.data["time"].iloc[-3] == pd.Timestamp("2011-01-01 23:54:00")
    assert int_cat.data["time"].iloc[-4] == pd.Timestamp("2011-01-01 23:53:45")
    assert int_cat.data["time"].iloc[-5] == pd.Timestamp("2011-01-01 23:53:30")


def test_pick_init():
    dir = "./tests/ExamplePos"
    stas = ["la01", "la05"]
    years = ["2010", "2011"]
    interpolation_time = 15
    max_gap_len = 120

    cats = []
    for sta in stas:
        cat = Catalog.Datastream(os.path.join(dir, sta), sta, years, interpolation_time)
        cat.findgaps(interpolation_time, max_gap_len)
        cats.append(cat)

    picks = Catalog.Picks(cats)
    assert picks.stas == cats


def test_lls_detection():
    dir = "./tests/ExamplePos"
    stas = ["la01", "la05"]
    years = ["2010", "2011"]
    interpolation_time = 15
    max_gap_len = 120

    cats = []
    for sta in stas:
        cat = Catalog.Datastream(os.path.join(dir, sta), sta, years, interpolation_time)
        cat.findgaps(interpolation_time, max_gap_len)
        cats.append(cat)

    picks = Catalog.Picks(cats)

    with pytest.raises(Exception) as e_info:
        picks.lls_detection(600, 17)
    assert str(e_info.value) == "Increment / Slide not an Integer"

    # picked = unpicked.lls_detection(600, 25)
