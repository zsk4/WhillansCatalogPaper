import src.Tides as Tides  # type: ignore
import datetime
import numpy as np
import pytest

# Slow marker is used for tests that require local file access to get the
# downloaded tidal model.


def test_init():
    model_loc = "/mnt/c/Users/ZacharyKatz/Desktop/Research/Background"
    model = "CATS2008-v2023"

    tide_mod = Tides.Tide(model_loc=model_loc, model=model)

    assert tide_mod.model == model
    assert tide_mod.model_loc == model_loc


@pytest.mark.slow
def test_tidal_elevation():
    # Set initial, final, and interval for tidal timeseries
    initial_time = datetime.datetime.strptime(
        "2010-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    final_time = datetime.datetime.strptime("2010-01-01 01:00:00", "%Y-%m-%d %H:%M:%S")
    interval = 5  # Minutes

    # Set where to calculate tides
    lats = [-84.2986]
    lons = [-164.5206]

    # Set model location
    model_loc = "/mnt/c/Users/ZacharyKatz/Desktop/Research/Background"
    model = "CATS2008-v2023"

    tide_mod = Tides.Tide(model_loc=model_loc, model=model)

    interval_sec = interval * 60
    # Calculate number of entries
    n = int((final_time - initial_time).total_seconds() / interval_sec)
    dates_timeseries = np.zeros(n, dtype=datetime.datetime)

    # Fill timeseries
    dates_timeseries = [
        initial_time + datetime.timedelta(minutes=interval * n) for n in range(n)
    ]

    # Model Tides
    full_model = tide_mod.tidal_elevation(lons, lats, dates_timeseries, multiloc=False)
    print(full_model)
