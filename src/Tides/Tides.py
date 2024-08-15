"""
Antarctic Tidal Calculations using CATS2008 [1,2].

Functions
---------
tidal_elevation
    Calculate the tidal elevation at the given locations and times.

References
----------
[1] Padman, L., Erofeeva, S. Y., & Fricker, H. A. (2008). Improving Antarctic
tide models by assimilation of ICESat laser altimetry over ice shelves.
Geophysical Research Letters, 35(22). https://doi.org/10.1029/2008GL035592
[2] Padman, L., Fricker, H. A., Coleman, R., Howard, S., & Erofeeva, L. (2002).
A new tide model for the Antarctic ice shelves and seas. Annals of Glaciology,
34, 247–254. https://doi.org/10.3189/172756402781817752
"""

import numpy as np
import pyTMD  # type: ignore
import xarray as xr
import timescale  # type: ignore


class Tide:
    """
    An instance of class Tides determines the tidal model to use and its location.
    """

    def __init__(self, model: str, model_loc: str) -> None:
        """Initialize a tidal model

        Parameters
        ----------
        model : str
            Model to pull tides from
        model_loc : str
            Location of model file
        """
        self.model = model
        self.model_loc = model_loc

    def tidal_elevation(self, lons: list, lats: list, datetimes: list) -> xr.DataArray:
        """
        Calculate the tidal elevation at the given locations and times. Adapted
        from pyTMD example: https://github.com/tsutterley/pyTMD/blob/main/notebooks/Plot%20Tide%20Forecasts.ipynb
        Choose to use pyTMD map or pyTMD time_series functions based on relative
        lengths of lons and datetimes

        Parameters
        ----------
        lons : list
            Longitudes for tide calculation
        lats : list
            Latitudes for tide calculation
        datetimes : list
            Times for tide calculation

        Returns
        -------
        tides : xarray.DataArray
            Tides [cm] at each location (lon, lat) and time (t).
        """

        # Convert dates to date since 01 Jan 1992 [The format pyTMD wants it in]
        years = np.array([date.year for date in datetimes])
        months = np.array([date.month for date in datetimes])
        days = np.array([date.day for date in datetimes])
        hours = np.array([date.hour for date in datetimes])
        minutes = np.array([date.minute for date in datetimes])
        # tide_time = pyTMD.time.convert_calendar_dates(
        #    year=years, month=months, day=days, hour=hours, minute=minutes
        # )
        tide_time = timescale.time.convert_calendar_dates(
            year=years, month=months, day=days, hour=hours, minute=minutes
        )

        # Setup model
        model = pyTMD.io.model(self.model_loc, format="netcdf").elevation(self.model)
        constituents = pyTMD.io.OTIS.read_constants(
            model.grid_file,
            model.model_file,
            model.projection,
            type=model.type,
            grid=model.format,
        )
        c = constituents.fields
        DELTAT = np.zeros_like(tide_time)
        amp, ph, D = pyTMD.io.OTIS.interpolate_constants(
            np.atleast_1d(lons),
            np.atleast_1d(lats),
            constituents,
            model.projection,
            type=model.type,
            method="spline",
            extrapolate=True,
        )

        # Complex phase and constituent oscillation
        cph = -1j * ph * np.pi / 180.0
        hc = amp * np.exp(cph)

        if len(lons) > 1:
            tide_holder = []
            for i in range(len(datetimes)):
                tide = self.tidal_elevation_map(tide_time[i], hc, c, DELTAT[i], model)
                tide_holder.append(tide)
        else:
            tide_holder = self.tidal_elevation_time_series(
                tide_time, hc, c, DELTAT, model
            )
            tide_holder = np.atleast_2d(tide_holder).T

        # Put in xarray
        obj_arr = [LatLon(lat, lon) for lat, lon in zip(lats, lons)]
        tides = xr.DataArray(
            dims=("t", "lat_lon"),
            coords={"t": datetimes, "lat_lon": obj_arr},
            data=tide_holder,
            attrs=dict(
                description="Tide Height",
                units="cm",
            ),
        )

        return tides

    @staticmethod
    def tidal_elevation_map(
        tide_time: float, hc: list, c: list, delat: float, model: pyTMD.io.model
    ) -> np.ndarray:
        """Use pyTMD's map function if more lat long pairs than times:

        Parameters
        ----------
        tide_time : float
            Tide time in pyTMD format
        hc : list
            Harmonic constants
        c : list
            Constituent ids
        delat : float
            Time correction
        model : pyTMD.io.model
            pyTMD model to use

        Returns
        -------
        np.ndarray
            Tide elevations at each location and time in m
        """

        # Predict tides and minor corrections
        TIDE = pyTMD.predict.map(
            tide_time, hc, c, deltat=delat, corrections=model.format
        )
        MINOR = pyTMD.predict.infer_minor(
            tide_time, hc, c, deltat=delat, corrections=model.format
        )
        TIDE.data[:] += MINOR.data[:]
        TIDE.data[:] *= 100.0  # Convert to cm
        return TIDE

    @staticmethod
    def tidal_elevation_time_series(
        tide_time: list, hc: list, c: list, delat: float, model: pyTMD.io.model
    ):
        """Use pyTMD's time_series function if more lat long pairs than times:

        Parameters
        ----------
        tide_time : list
            Tide times in pyTMD format
        hc : list
            Harmonic constants
        c : list
            Constituent ids
        delat : float
            Time correction
        model : pyTMD.io.model
            pyTMD model to use
        Returns
        -------
        np.ndarray
            Tide elevations at each location and time in m
        """
        # Predict tides and minor corrections
        TIDE = pyTMD.predict.time_series(
            tide_time, hc, c, deltat=delat, corrections=model.format
        )
        MINOR = pyTMD.predict.infer_minor(
            tide_time, hc, c, deltat=delat, corrections=model.format
        )
        TIDE.data[:] += MINOR.data[:]
        TIDE.data[:] *= 100.0  # Convert to cm
        return TIDE


class LatLon:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
