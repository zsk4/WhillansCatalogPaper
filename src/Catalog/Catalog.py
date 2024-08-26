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
from typing import Tuple, Self, Any
import warnings
import scipy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


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

        # Filled in when interpolation is run
        self.starts: list[datetime.datetime] = []
        self.ends: list[datetime.datetime] = []
        self.gaps: list[datetime.timedelta] = []

        # Filled in when lls_detection is run
        self.residuals = None
        self.xs = None
        self.ys = None
        self.zs = None
        self.times = None

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

        Assumes data in 00,15,30,45 second and removes all other data.
        For slw1, 46 second data are moved to 45 seconds.
        Note this will fail if Secondly data is provided (i.e. data at both 45 and 46 seconds)
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
                | d["HR:MN:SS.SS"].str.endswith("16.00")  # Slw1 only, move to 15 sec
                | d["HR:MN:SS.SS"].str.endswith("46.00")  # Slw1 only, move to 45 sec
            ]
            data["longitude"] = d["LONDD"] - d["LONMN"] / 60 - d["LONSS"] / 60 / 60
            data["latitude"] = d["LATDD"] - d["LATMN"] / 60 - d["LATSS"] / 60 / 60
            data["time"] = pd.to_datetime(d["YEAR-MM-DD"] + "T" + d["HR:MN:SS.SS"])
            data.loc[data["time"].dt.second == 46, "time"] = data[
                "time"
            ] - pd.Timedelta(seconds=1)  # Slw1 only, move to 45 sec
            data.loc[data["time"].dt.second == 16, "time"] = data[
                "time"
            ] - pd.Timedelta(seconds=1)  # Slw1 only, move to 15 sec
            data["day_of_year"] = d["DAYofYEAR"]

        # If not in 2024 format, may be in an older format, tested for below...
        except Exception as e:
            try:
                logger.warning(f"Position file not from 2024 CSRS-PPP run: {e}")
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
                    logger.warning(f"Position file not from 2024 CSRS-PPP run: {e}")
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
                    logger.warning(f"Position file not from 2024 CSRS-PPP run: {e}")
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

        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            data = data.interpolate(method="linear")  # Built-in pandas function
        return data

    def findgaps(self, max_gap_len: int) -> Self:
        """
        Finds gaps in a dataframe loaded with datastream. Returns interpolated data
        and two arrays corresponding to the start entry and the length of the gap

        Input Paramerers
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
        _data = None
        # Time (in seconds, inclusive) to allow interpolation before shutting off
        starts.append(data["time"].iloc[0])
        for i in data.index:
            # Check not first element
            if i > 0:
                prior_date = data["time"][i - 1]
                date = data["time"][i]
                # Check if time between dates is not less than 16 seconds
                # Choose 16 to catch weird 15 second gaps like 15.00003
                gaptime = self.interpolation_time + 1
                if date - prior_date > datetime.timedelta(seconds=gaptime):
                    gap = date - prior_date

                    # If gap interpolatable, call interpolate and add to df else
                    # note gap start, end, and length then continue.
                    if gap <= datetime.timedelta(seconds=max_gap_len):
                        # Find number of elements needed to be interpolated, using
                        # gap length // 15 seconds,
                        interpolate_elements = int(
                            gap.total_seconds() // self.interpolation_time
                        )
                        logger.info(f"{prior_date} {date} {gap}")
                        _data = self.interpolate(
                            prior_date, date, gap, i, interpolate_elements
                        )
                    else:
                        starts.append(date)
                        ends.append(prior_date)
                        gaps.append(gap)

        ends.append(data["time"].iloc[-1])
        if _data is not None:
            self.data = _data
        self.starts = starts
        self.ends = ends
        self.gaps = gaps

        return self


class Picks:
    """Picked Events for A Set of Data Streams"""

    def __init__(self, stas: list) -> None:
        """Initialize a set of data streams to pick events from

        Parameters
        ----------
        stas: list of Datastream objects
            List of data streams to pick events from
        """
        self.stas = stas

    def lls_detection(self, increment: int, slide: int) -> None:
        """Linear least squares resiudal detection of stick slip events

        Parameters
        ----------
        increment: int
            Data points to perform the regression on
        slide: int
            Data points to slide the window each cyclewith pytest.raises(Exception) as e_info:
        """
        # Perform using actual times rather than number of data points to accommodate la02's 30 second increments

        # Look for a more scientific way to choose variables increment and slide
        # besides what gives the best event detections.

        # Loop for each station z
        for z, sta in enumerate(self.stas[:]):
            name = sta.name
            logger.info(f"Linear Least Squares on {name}")
            times = []
            xs = []
            ys = []
            zs = []
            residuals = []

            # Make increment and slide match that for 15 second data
            dividing_factor = sta.interpolation_time // 15
            increment = increment // dividing_factor
            slide = slide // dividing_factor
            # print(name, increment, slide)
            if increment % slide != 0:
                raise Exception("Increment / Slide not an Integer")

            # Loop over each start and end time
            for st, en in zip(sta.starts, sta.ends):
                # Get index of data at start and end times
                start = sta.data.loc[sta.data["time"] == st].index[0]
                end = sta.data.loc[sta.data["time"] == en].index[0]
                length = end - start
                if length != 0:
                    # Mark current start and end for averaging
                    start_pos = 0
                    end_pos = start_pos + increment
                    first_entry = sta.data.iloc[start].name

                    time_arr = sta.data["time"][start:end].reset_index(drop=True)
                    x_arr = sta.data["x"][start:end].reset_index(drop=True)
                    y_arr = sta.data["y"][start:end].reset_index(drop=True)
                    z_arr = sta.data["elevation"][start:end].reset_index(drop=True)
                    xs.append(x_arr)
                    ys.append(y_arr)
                    zs.append(z_arr)
                    times.append(time_arr)

                    time_in_sec = np.zeros(length)
                    for i in range(length):
                        time_in_sec[i] = (
                            sta.data["time"][first_entry + i]
                            - datetime.datetime(2000, 1, 1)
                        ).total_seconds()  # Get time from 2000

                    # Find the linear least square average at each window
                    averaging_pts = np.zeros(length // slide)
                    for i in range((length // slide) - increment // slide):
                        box = np.zeros(length)
                        box[start_pos:end_pos] = 1
                        func = np.multiply(sta.data["x"][start:end], box)  # Summation
                        func = func[start_pos:end_pos]
                        M = np.ones((len(func), 2))
                        M[:, 1] = time_in_sec[start_pos:end_pos]
                        p, res, rnk, s = scipy.linalg.lstsq(M, func)
                        averaging_pts[i] = res
                        start_pos += slide
                        end_pos += slide

                    # Create residual array by using average at each point
                    residual_arr = np.zeros(length)

                    start_pos = 0
                    end_pos = start_pos + increment
                    first_entry = sta.data.iloc[start].name

                    num = increment // slide
                    for i in range(length // slide):
                        if i > increment // slide:
                            avg = 0
                            for j in range(i - num, i):
                                avg = avg + averaging_pts[j]
                            residual_arr[start_pos:end_pos] = avg / num
                        start_pos += slide
                        end_pos += slide
                    residuals.append(residual_arr)

            sta.residuals = residuals
            sta.xs = xs
            sta.ys = ys
            sta.zs = zs
            sta.times = times

    def merge(self) -> pd.DataFrame:
        """Make mega dataframe with all traces and Nan if station not operating

        Parameters
        ----------

        Returns
        merged: pd.DataFrame
            Mega dataframe with all traces

        """
        # Make individual dataframes to merge and merge dataframes
        for iter, sta in enumerate(self.stas):
            # print(iter,sta.name)
            flat_times = []
            for xs in sta.times:
                for x in xs:
                    flat_times.append(x)
            flat_xs = []
            for xs in sta.xs:
                for x in xs:
                    flat_xs.append(x)
            flat_res = []
            for xs in sta.residuals:
                for x in xs:
                    flat_res.append(x)
            flat_ys = []
            for xs in sta.ys:
                for x in xs:
                    flat_ys.append(x)
            df = pd.DataFrame(
                {
                    "time": flat_times,
                    sta.name + "x": flat_xs,
                    sta.name + "y": flat_ys,
                    sta.name + "res": flat_res,
                }
            )
            if iter == 0:
                merged = df
            if iter >= 1:
                merged = merged.merge(df, how="outer", on="time")

        merged = merged.sort_values(by="time", ignore_index=True)
        if "la02res" in merged.columns:
            merged["la02res"] = merged["la02res"].interpolate(method="linear", limit=1)
            merged["la02x"] = merged["la02x"].interpolate(method="linear", limit=1)
        return merged

    def on_off_list(self) -> pd.DataFrame:
        """Get sorted list of onsets and offsets

        Parameters
        ----------
        Returns
        sorted_list: pd.DataFrame
            Sorted list of onsets and offsets

        """
        # Get sorted list of onsets and offsets
        start_end = pd.DataFrame(columns=["times", "onset", "station"])

        for sta in self.stas:
            for time_arr in sta.times:
                start_end.loc[len(start_end)] = [time_arr[0], True, sta.name]
                start_end.loc[len(start_end)] = [
                    time_arr[len(time_arr) - 1],
                    False,
                    sta.name,
                ]

        sorted_list = start_end.sort_values(
            by=["times", "onset"], ascending=[True, False]
        ).reset_index(drop=True)

        return sorted_list

    def no_data_csv(self, sorted: pd.DataFrame) -> pd.DataFrame:
        """Export csv with times of no data

        Parameters
        ----------
        sorted: pd.DataFrame
            Sorted list of onsets and offsets made by on_off_list

        Returns
        df_no_data: pd.DataFrame
            Dataframe of no data times
        """
        on_stas = 0
        prior_on_stas = 0
        start_no_data = []
        end_no_data = []
        for i, row in enumerate(sorted.iterrows()):
            if row[1]["onset"] is True:
                on_stas += 1
            if row[1]["onset"] is False:
                on_stas -= 1
            if i >= 1:
                if prior_on_stas == 2 and on_stas == 1:
                    start_no_data.append(row[1]["times"])
                if prior_on_stas == 1 and on_stas == 2:
                    end_no_data.append(row[1]["times"])
            prior_on_stas = on_stas

        st_year = self.stas[0].years[0]
        end_year = self.stas[0].years[-1]

        # If no data starting at end of timeframe, remove
        if start_no_data[-1] >= datetime.datetime(int(end_year), 12, 31, 23, 59, 00):
            start_no_data.pop()
        else:
            end_no_data.append(pd.Timestamp(int(end_year), 12, 31, 23, 59, 45))

        # If no data starting at start of timeframe, remove
        if end_no_data[0] <= datetime.datetime(int(st_year), 1, 1, 00, 1, 00):
            end_no_data.pop(0)
        else:
            start_no_data.insert(0, pd.Timestamp(int(st_year), 1, 1, 00, 00, 00))

        df_no_data = pd.DataFrame({"start": start_no_data, "end": end_no_data})

        df_no_data.to_csv(f"{st_year}-{end_year}no_data.txt", index=False, sep="\t")
        return df_no_data


class Events:
    """Catalog of Events"""

    def __init__(self, merged: pd.DataFrame) -> None:
        """Initialize a catalog of events

        Parameters
        ----------
        merged: pd.DataFrame
            Mega dataframe with all traces
        """
        self.merged = merged

    def on_off_indices(self, sorted: pd.DataFrame) -> list:
        """Get a of indices of when stations turn on/off

        Parameters
        ----------
        sorted: pd.DataFrame
            Sorted list of onsets and offsets made by on_off_list

        Returns
        indices: list
            List of indices of when stations turn on/off

        """
        indices = []
        for time in sorted["times"]:
            index = self.merged.index[self.merged["time"] == time][0]
            indices.append(index)
        return indices

    def pick_events(self, sorted: pd.DataFrame, active_stas: int) -> float:
        """Get a of indices of when stations turn on/off. Updates Events in place

        Parameters
        ----------
        sorted: pd.DataFrame
            Sorted list of onsets and offsets made by on_off_list
        active_stas: int
            Minimum required number of active stations to consider an event

        Returns
        thresh: float
            Threshold value of summed residual for event detection
        """

        # For 2007-2009 I used thresh = avg + 0.5 * std
        # and checked to ensure both traces were active.
        # For 2010-2019 I used thresh = avg
        logger.info("Picking Events")
        # Find combined least square residual for each time block O(10 min)
        res_cols = [col for col in self.merged if str(col).endswith("res")]
        x_cols = [col for col in self.merged if str(col).endswith("x")]

        self.merged["ressum"] = self.merged[res_cols].sum(axis=1)
        # Use the peaks and an average thresholding algortihm to pick out the events.
        avg = np.average(self.merged["ressum"])
        std = np.std(self.merged["ressum"])
        logger.info(f"Average: {avg}, Standard Deviation: {std}")

        event = np.zeros(len(self.merged["ressum"]))
        thresh = avg  # Threshold choice here e.g, avg + std
        x_col_check = active_stas - 1  # Indexed at 0 so subtract 1
        for i in range(len(event)):
            nansum = 0
            for col in x_cols:
                nan_check = self.merged[col][i]
                if np.isnan(nan_check):
                    nansum += 1
            if (
                self.merged["ressum"][i] > thresh and nansum < len(x_cols) - x_col_check
            ):  # Check at least two non-nan cols
                event[i] = 1
        self.merged["event"] = event

        return thresh

    def plot_picking(
        self,
        indices: list,
        thresh: float,
        num_plots: int,
    ) -> None:
        """Plot events until the nth gap.

        Parameters
        ----------
        indices : list
            List of indices of when stations turn on/off
        num_plots : int
            Number of plots to make
        thresh : float
            Threshold value of summed residual for event detection
        """
        merged = self.merged
        x_cols = [col for col in merged if str(col).endswith("x")]
        for i, index in enumerate(indices[:num_plots]):
            if i > 0:
                if indices[i - 1] != indices[i]:
                    start = indices[i - 1]
                    end = index

                    fig, ax1 = plt.subplots(figsize=(14, 8))
                    colors = [
                        "#1f77b4",
                        "#ff7f0e",
                        "#2ca02c",
                        "#d62728",
                        "#9467bd",
                        "#8c564b",
                        "#e377c2",
                        "#7f7f7f",
                        "#7f7f7f",
                        "#17becf",
                        "#1f77b4",
                        "#ff7f0e",
                        "#2ca02c",
                        "#d62728",
                        "#9467bd",
                        "#8c564b",
                        "#e377c2",
                        "#7f7f7f",
                        "#bcbd22",
                        "#17becf",
                        "#1f77b4",
                        "#ff7f0e",
                        "#2ca02c",
                        "#d62728",
                        "#9467bd",
                        "#8c564b",
                        "#e377c2",
                        "#7f7f7f",
                        "#bcbd22",
                        "#17becf",
                    ]
                    colors = [
                        "dimgray",
                        "gray",
                        "darkgray",
                        "silver",
                        "lightgray",
                        "gainsboro",
                        "dimgray",
                        "gray",
                        "darkgray",
                        "silver",
                        "lightgray",
                        "gainsboro",
                        "dimgray",
                        "gray",
                        "darkgray",
                        "silver",
                        "lightgray",
                        "gainsboro",
                        "dimgray",
                        "gray",
                        "darkgray",
                        "silver",
                        "lightgray",
                        "gainsboro",
                        "dimgray",
                        "gray",
                        "darkgray",
                        "silver",
                        "lightgray",
                        "gainsboro",
                        "dimgray",
                        "gray",
                        "darkgray",
                        "silver",
                        "lightgray",
                        "gainsboro",
                    ]
                    for j, x_col in enumerate(x_cols):
                        # print(i)
                        ax1.plot(
                            merged["time"][start:end],
                            merged[x_col][start:end]
                            - np.mean(merged[x_col][start:end])
                            - np.ones_like(merged[x_col][start:end])
                            * (
                                merged[x_col][start] - np.mean(merged[x_col][start:end])
                            ),
                            color=colors[j],
                        )
                    ax1.set_ylabel("Station $\Delta$X [meters]", size=20, color="gray")
                    ax1.set_xlabel("Date", size=20)
                    ax2 = ax1.twinx()
                    rd = (160 / 255, 56 / 255, 32 / 255)
                    ax2.plot(
                        merged["time"][start:end], merged["ressum"][start:end], color=rd
                    )
                    ltred = (237 / 255, 179 / 255, 165 / 255)
                    ax2.plot(
                        merged["time"][start:end],
                        np.ones_like(merged["ressum"][start:end]) * thresh,
                        color=ltred,
                    )
                    ax2.set_ylabel(
                        "Least Squares Residual [Sliding Window]", size=20, color=rd
                    )
                    ax3 = ax1.twinx()
                    ax3.set_axis_off()
                    masked: np.typing.NDArray[Any] = np.ma.masked_array(
                        merged["event"][start:end],
                        mask=(1 - merged["event"][start:end]),
                    )
                    ax3.plot(
                        merged["time"][start:end], masked, color="#0047AB", linewidth=5
                    )
                    ax3.plot(
                        merged["time"][start:end],
                        np.zeros_like(merged["time"][start:end]),
                        alpha=0,
                    )
                    ax1.tick_params(axis="y", labelsize=15, labelcolor="gray")
                    ax2.tick_params(axis="y", labelsize=15, labelcolor="#0047AB")
                    ax1.tick_params(axis="x", labelsize=15)
                    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                    ax1.xaxis.set_major_locator(mdates.MonthLocator())

    def make_catalog(self, cull_time: int, cull_dist: float) -> list:
        """Make the event catalog and cull to events longer than x min

        Parameters
        ----------
        cull_time : int
            Cull events less than cull_time minutes long
        cull_dist : float
            Cull events with min delta_x < cull_dist [meters]

        Returns
        -------
        rev_catalog : list
            Catalog events (dataframes) that survived the culling
        """

        start_indices = []
        end_indices = []
        for i, event in enumerate(self.merged["event"]):
            if i >= 1:
                prior_i = self.merged["event"][i - 1]
                if prior_i < event:
                    start_indices.append(i)
                elif prior_i > event:
                    end_indices.append(i)

        catalog = np.empty(len(start_indices), dtype="object_")

        x = 0
        for s, e in zip(start_indices, end_indices):
            catalog[x] = self.merged.iloc[s:e]
            x += 1

        # Initial cull of catalog by removing all false events less than cull_time
        cull_time_catalog = []
        for event in catalog:
            start = event.iloc[0]["time"]
            end = event.iloc[-1]["time"]
            if end - start > datetime.timedelta(minutes=cull_time):
                cull_time_catalog.append(event)

        # Second cull of catalog removing all events with min delta_x < cull_dist
        cull_dist_catalog = []
        for event in cull_time_catalog:
            x_cols = [col for col in catalog[0] if str(col).endswith("x")]
            end_avg = 0.0
            for x_col in x_cols:
                if not np.isnan(event[x_col].iloc[-1]):
                    # Demean to 0 at start
                    end_val = (
                        event[x_col].iloc[-1]
                        - np.mean(event[x_col])
                        - (event[x_col].iloc[0] - np.mean(event[x_col]))
                    )
                    end_avg += end_val
            end_avg = end_avg / len(x_cols)
            if end_avg > cull_dist:
                cull_dist_catalog.append(event)

        rev_catalog = cull_dist_catalog
        return rev_catalog


def save_catalog(rev_catalog: list, dir_save: str) -> None:
    """Save rev_catalog data frames as txt files

    Parameters
    ----------
    rev_catalog : list
        List of dataframes to save
    dir_save : str
        Directory to save to
    """
    for event in rev_catalog:
        timestamp = event["time"].iloc[0]
        datestring = "_".join(str(timestamp).split())
        datestring = datestring.replace(":", "-")
        output_dir = Path(dir_save)
        output_dir.mkdir(parents=True, exist_ok=True)
        event.to_csv(f"{dir_save}/{datestring}.evt", sep="\t")


def plot_event(event_to_plot: pd.DataFrame) -> None:
    """
    Plot a single event from the catalog

    event_to_plot: Catalog Number of Event To Plot
    """

    # res_cols = [col for col in merged if col.endswith('res')]
    x_cols = [col for col in event_to_plot if str(col).endswith("x")]
    fig, ax1 = plt.subplots()
    first = True
    for i, x_col in enumerate(x_cols):
        demeaned_to_0 = (event_to_plot[x_col] - np.mean(event_to_plot[x_col])) - (
            event_to_plot[x_col][event_to_plot.index[0]] - np.mean(event_to_plot[x_col])
        )
        if not np.isnan(event_to_plot[x_col][event_to_plot.index[0]]):
            if first:
                ax2_dummy = demeaned_to_0
                first = False
            ax1.plot(event_to_plot["time"], demeaned_to_0, label=str(x_col)[:-1])
    ax1.set_ylabel("X Displacement [meters]")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.legend()

    # Setup dates using second axis
    ax2 = ax1.twiny()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
    fig.subplots_adjust(bottom=0.10)
    ax2.set_frame_on(True)
    ax2.patch.set_visible(False)
    ax2.xaxis.set_ticks_position("bottom")
    ax2.xaxis.set_label_position("bottom")
    ax2.spines["bottom"].set_position(("outward", 20))
    ax2.set_xlabel("DateTime")

    # Need to plot something on ax2 to getthe correct dates
    ax2.plot(event_to_plot["time"], ax2_dummy)
    for label in ax2.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)


def set_interpolation_time(sta, years) -> Tuple[int, bool]:
    """
    Determine what time to interpolate based on data frequency for the station.
    Default is 15 seconds, but there are some stations that have different frequencies.

        # List of Stations with data not in 15 sec increments

        # la02 | 2008 - 7 JAN 2014 (la020070) 30 sec
        # slw1 | 2009 - 2010 02 sec Currently Ignored in processing
        # la14 | 2017???? 30 sec
        # la09 | 2010 - 5 FEB 2010 (la090310) 30 sec
        # whl02,03,07,09,11 only in xyzt format and no rinex, currently not used

    Parameters
    ----------
    sta: str
        Station name
    years: list of strings
        Years to be run

    Returns
    interpolation_time: int
        Interpolation time in seconds to be used for sta during years.
    run: bool
        Whether or not to run the station during the years.
    """

    interpolation_time = 15
    run = True

    if sta == "la02" and (
        "2008"
        or "2009"
        or "2010"
        or "2011"
        or "2012"
        or "2013"
        or "2014_30Sec" in years
    ):
        interpolation_time = 30
    elif sta == "la09" and ("2010" in years):
        interpolation_time = 30

    return interpolation_time, run
