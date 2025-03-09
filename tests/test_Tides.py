import src.Tides.Tides as Tides
import pytest
import datetime
import numpy as np


# Currently loads local CATS2008_v2023.nc model file because downloading from
# USAP-DC requires a captcha. Tyler's work around is to use AWS.abs

# Thus, tests marked this file as @pytest.mark.slow are only run when pytest
# is run locally, before committing.


def test_init():
    model_loc = "/mnt/c/Users/ZacharyKatz/Desktop/Research/Background"
    model = "CATS2008-v2023"

    tide_mod = Tides.Tide(model_loc=model_loc, model=model)

    assert tide_mod.model == model
    assert tide_mod.model_loc == model_loc


@pytest.mark.slow
def test_tidal_elevation_time_series():
    # Set initial, final, and interval for tidal timeseries
    initial_time = datetime.datetime.strptime(
        "2010-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    final_time = datetime.datetime.strptime("2010-01-01 0:30:00", "%Y-%m-%d %H:%M:%S")
    interval = 10  # Minutes

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
    model = tide_mod.tidal_elevation(lons, lats, dates_timeseries)
    expected_data = [-133.3843213881168, -133.55588749711248, -133.353938827298]
    expected_times = [
        np.datetime64("2010-01-01T00:00"),
        np.datetime64("2010-01-01T00:10"),
        np.datetime64("2010-01-01T00:20"),
    ]
    for tide, time, expected_dat, expected_time in zip(
        model.data, model.t.data, expected_data, expected_times
    ):
        assert tide == expected_dat
        assert time - expected_time == np.timedelta64(0, "s")
    assert model.lat_lon.data[0].lat == -84.2986
    assert model.lat_lon.data[0].lon == -164.5206


@pytest.mark.slow
def test_tidal_elevation_map():
    # Set initial, final, and interval for tidal timeseries
    initial_time = datetime.datetime.strptime(
        "2010-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    final_time = datetime.datetime.strptime("2010-01-01 00:20:00", "%Y-%m-%d %H:%M:%S")
    interval = 10  # Minutes

    # Set where to calculate tides
    lats = [-84.2986, -84.2989]
    lons = [-164.5206, -164.5209]

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
    model = tide_mod.tidal_elevation(lons, lats, dates_timeseries)
    expected_data = [-133.3843213881168, -133.38489077117055]
    expected_times = [np.datetime64("2010-01-01T00:00")]
    for tide, time, expected_data, expected_time in zip(
        model.data[0], model.t.data, expected_data, expected_times
    ):
        print(tide, time, expected_data, expected_time)
        assert tide == expected_data
        assert time - expected_time == np.timedelta64(0, "s")
    assert model.lat_lon.data[0].lat == -84.2986
    assert model.lat_lon.data[0].lon == -164.5206
    assert model.lat_lon.data[1].lat == -84.2989
    assert model.lat_lon.data[1].lon == -164.5209
