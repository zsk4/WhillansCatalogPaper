"""
Automatic Picking of Whillans Stick Slip Events

Zachary Katz
zachary_katz@mines.edu
August 2024

Requires processed gps .pos files in folders labeled with station name and year
at directory given by string 'dir' (see cell labeled # Main). This is currently
coded on the MGL_1 external hard drive, or D drive.

Example Directory Tree:
--------------------------------------------------------------------------------
↳la01
    ↳2010
        ↳la010150.pos
            la010160.pos
        ...
    ↳2011
        ...
↳la02
    ...
--------------------------------------------------------------------------------

Precise point solution files are from Natural Resources Canada, Geodetic Survey
Division, Geomatics Canada, and processed at several different times, resulting
in several differences in how the data within a file is structured; these are
handled by try except statements.

Functions
---------
ll2xy
    Converts longitude and latitude to Antarctic Polar Stereographic

"""

from pyproj import CRS, Transformer
import os
import pandas as pd
import numpy as np
import datetime
from typing import Tuple, Self
import warnings


def ll2xy(lon, lat):
    """
    Transform coordinates from input geodetic coordinates (lon, lat)
    to output Antarctic Polar Stereographic coordinates (x, y)

    Parameters
    lon - Geodetic longitude in EPSG:4326 [float]
    lat - Geodetic latitude in EPSG:4326 [float]

    Returns
    x - Antarctic Polar Stereographic (EPSG:3031) x [float]
    y - Antarctic Polar Stereographic (EPSG:3031) y [float]
    """

    crs_ll = CRS("EPSG:4326")
    crs_xy = CRS("EPSG:3031")
    ll_to_xy = Transformer.from_crs(crs_ll, crs_xy, always_xy=True)
    x, y = ll_to_xy.transform(lon, lat)
    return x, y


class Datastream:
    """Data for one station"""

    def __init__(
        self, sta: os.DirEntry, name: str, years: list, interpolation_time: int
    ) -> None:
        """Initialize a data stream.

        Parameters
        ----------
        sta: os.DirEntry
            Path to station
        name : str
            Name of the station (Typically the directory name)
        years : list
            List of year folders to include in this data stream.
        interpolation_time : int
            Time in seconds for interpolation [la01 15 sec, la02 30 sec, etc.]
        """
        self.sta = sta
        self.name = name
        self.years = years
        self.interpolation_time = interpolation_time

        data = self.make_data_stream(sta, years)
        self.data = data

    def make_data_stream(self, sta: os.DirEntry, years: list) -> pd.DataFrame:
        """
        Return a Pandas data frame for all .pos files in years.

        Takes input directory sta with year subdirectories containing .pos files.
        Starting from the first file in the first year, append days until all files
        in the directory have been added.

        Parameters
        ----------
        dir: os.DirEntry
            Input directory tree with structure described in top comment [string]
        years: list of strings
            Years to be run

        Returns
        data: pd.DataFrame
            Multi-day data frame
        """

        data = pd.DataFrame()
        for year in years:
            for folder in os.scandir(os.fspath(self.sta)):
                # Folder is an os.DirEntry object
                if folder.is_dir():
                    if folder.name == year:
                        for gps in sorted(os.listdir(folder.path)):
                            # Ignore xyzt, zip files
                            if gps.endswith(".pos") and not gps.startswith("."):
                                ind_data, flip = self.load(f"{folder.path}/{gps}")
                                # Reorder the data if using CSRS-PPP 2024 pre 2018
                                if flip:
                                    ind_data = ind_data.reindex(
                                        index=ind_data.index[::-1]
                                    )
                                data = pd.concat([data, ind_data], ignore_index=True)
        return data

    def load(self, file: str) -> Tuple[pd.DataFrame, bool]:
        """
        Load processed gps data file into pandas table.

        Parameters
        file - .pos precise point solution file, Natural Resources Canada [string]

        Returns
        data - Pandas DataFrame with the following columns, extracted from file
            longitude - Geodetic longitude
            latitude - Geodetic latitude
            elevation - Elevation
            time - Time as datetime object
            day_of_year - Time as julian day
            x - Antarctic Polar Stereographic x
            y - Antarctic Polar Stereographic y
            dist - Euclidian distance from starting position in meters
        flip - flag to flip order of readings for 2024 csrs-ppp data
        """

        data = pd.DataFrame()  # Create Pandas DataFrame
        flip = False
        # Read data file

        # Convert longitude and latitude from deg min sec to fractional degrees
        # Three different file formats so try one first and try the other if it
        # throws a not found exception.
        try:
            # CSRS-PPP 2024
            d = pd.read_csv(
                file, skiprows=3, sep="\\s+"
            )  # delim_whitespace=True depreciated, used \\s+ instead
            # Only take 15 or 30 sec intervals if data is finer spaced
            d = d.loc[
                d["HR:MN:SS.SS"].str.endswith("00.00")
                | d["HR:MN:SS.SS"].str.endswith("15.00")
                | d["HR:MN:SS.SS"].str.endswith("30.00")
                | d["HR:MN:SS.SS"].str.endswith("45.00")
            ]
            data["longitude"] = d["LONDD"] - d["LONMN"] / 60 - d["LONSS"] / 60 / 60
            data["latitude"] = d["LATDD"] - d["LATMN"] / 60 - d["LATSS"] / 60 / 60
            data["time"] = pd.to_datetime(d["YEAR-MM-DD"] + "T" + d["HR:MN:SS.SS"])
            data["day_of_year"] = d["DAYofYEAR"]

        # If not in 2024 format, may be in an older format, tested for below...
        except Exception as e:
            try:
                print(e)
                d = pd.read_csv(file, skiprows=7, sep="\\s+")
                data["longitude"] = (
                    d["LON(d)"] - d["LON(m)"] / 60 - d["LON(s)"] / 60 / 60
                )
                data["latitude"] = (
                    d["LAT(d)"] - d["LAT(m)"] / 60 - d["LAT(s)"] / 60 / 60
                )
                data["time"] = pd.to_datetime(d["YEAR-MM-DD"] + "T" + d["HR:MN:SS.SSS"])
                data["day_of_year"] = d["DOY"]
            except Exception as e:
                try:
                    print(e)
                    d = pd.read_csv(file, skiprows=5, sep="\\s+")
                    data["longitude"] = (
                        d["LONDD"] - d["LONMN"] / 60 - d["LONSS"] / 60 / 60
                    )
                    data["latitude"] = (
                        d["LATDD"] - d["LATMN"] / 60 - d["LATSS"] / 60 / 60
                    )
                    data["time"] = pd.to_datetime(
                        d["YEAR-MM-DD"] + "T" + d["HR:MN:SS.SS"]
                    )
                    data["day_of_year"] = d["DAYofYEAR"]
                except Exception as e:
                    print(e)
                    d = pd.read_csv(file, skiprows=6, sep="\\s+")
                    data["longitude"] = (
                        d["LON(d)"] - d["LON(m)"] / 60 - d["LON(s)"] / 60 / 60
                    )
                    data["latitude"] = (
                        d["LAT(d)"] - d["LAT(m)"] / 60 - d["LAT(s)"] / 60 / 60
                    )
                    data["time"] = pd.to_datetime(
                        d["YEAR-MM-DD"] + "T" + d["HR:MN:SS.SSS"]
                    )
                    data["day_of_year"] = d["DOY"]

        data["elevation"] = d["HGT(m)"]
        data["sats"] = d["NSV"]
        data["GDOP"] = d["GDOP"]

        # Check length before
        # Convert to Antarctic Polar Stereographic
        x, y = ll2xy(lon=data["longitude"], lat=data["latitude"])
        data["x"] = x
        data["y"] = y

        # Look at data and decide if to flip
        if len(data.index) > 1:
            diff = data["time"].iloc[0] - data["time"].iloc[1]
            if diff > datetime.timedelta(seconds=0):
                flip = True

            # Keep in if statement because fails if no data
            x0 = data["x"].iloc[0]
            y0 = data["y"].iloc[0]

            data["dist"] = np.sqrt((data["x"] - x0) ** 2 + (data["y"] - y0) ** 2)

        return data, flip

    def interpolate(
        self,
        prior_date: pd.Timestamp,
        date: pd.Timestamp,
        gap: pd.Timedelta,
        i: int,
        interpolate_elements: int,
    ) -> pd.DataFrame:
        """
        Interpolate the given data gap using Pandas' linear interpolation scheme.

        Input Parametrers
            data - PandasDataframe with time gaps [DataFrame]
            prior_data - last time entry before data gap [Datetime]
            date - first time entry after data gap [Datetime]
            gap - length of gap in seconds [Timedelta]
            i - DataFrame row index of first entry after data gap [integer]
            interpolate_elements - number of elements needed to be interpolated [integer]

        Returns
            data - interpolated DataFrame [DataFrame]
        """
        data = self.data
        # Loop over each missing row
        for row in range(interpolate_elements - 1):
            # Make data frame row
            insert = pd.DataFrame(columns=data.columns, index=[i + row])
            with warnings.catch_warnings():
                warnings.simplefilter(action="ignore", category=FutureWarning)
                data = pd.concat(
                    [data.iloc[: i + row], insert, data.iloc[i + row :]]
                ).reset_index(drop=True)
        data = data.interpolate(method="linear")  # Built-in pandas function
        return data

    def findgaps(self, gap_len: int, interpolate_time: int) -> Self:
        """
        Finds gaps in a dataframe loaded with datastream. Returns interpolated data
        and two arrays corresponding to the start entry and the length of the gap

        Input Paramerers
            data - DataFrame with or without gaps to interpolate [DataFrame]
            gap_len - the length of time of the base data
        Returns
            data - DataFrame that has been interpolated [DataFrame]
            starts - list of start times of uninterpolated data gaps (because they
                    were too long to interpolate) [Array of Datetimes]
            ends - list of end times of uninterpolated data gaps (because they
                    were too long to interpolate) [Array of Datetimes]
            gaps - list of lengths in seconds of uninterpolated data gaps (because
                    they were too long to interpolate) [Array of Timedeltas]
        """

        starts = []  # First Data point after gap
        ends = []  # Last data point before gap
        gaps = []  # Length of data [Start time - End time]

        data = self.data
        # Time (in seconds, inclusive) to allow interpolation before shutting off
        starts.append(data["time"].iloc[0])
        for i in data.index:
            # Check not first element
            if i > 0:
                prior_date = data["time"][i - 1]
                date = data["time"][i]

                # Check if time between dates is not less than 16 seconds
                # Choose 16 to catch weird 15 second gaps like 15.00003
                gaptime = gap_len + 1
                if date - prior_date > datetime.timedelta(seconds=gaptime):
                    gap = date - prior_date
                    # print(date,prior_date, i, gap)

                    # If gap interpolatable, call interpolate and add to df else
                    # note gap start, end, and length then continue.
                    if gap <= datetime.timedelta(seconds=interpolate_time):
                        # Find number of elements needed to be interpolated, using
                        # gap length // 15 seconds,
                        interpolate_elements = int(gap.total_seconds() // gap_len)
                        print(prior_date, date, gap, i)
                        datax = self.interpolate(
                            prior_date, date, gap, i, interpolate_elements
                        )
                    else:
                        starts.append(date)
                        ends.append(prior_date)
                        gaps.append(gap)

        ends.append(data["time"].iloc[-1])
        self.data = datax
        self.starts = starts
        self.ends = ends
        self.gaps = gaps

        return self
