"""
Wrapper for calling several catalog functions at once

Zachary Katz
zachary_katz@mines.edu
August 2024


"""

from . import Catalog  # In same folder as this file so no src.Catalog needed


def full_catalog_run(
    data: list,
    years: list,
    window: int,
    slide: int,
    active_stas: int,
    cull_time: int,
    plot: bool,
) -> list:
    """Wrapper function that goes from a list of Datastreams to a list of events

    Parameters
    ----------
    data : list
        List of Catalog.Datastream objects to be made into a catalog
    window : int
        Number of data points to perform the regression on
    slide: int
        Data points to slide the window each cycle
    active_stas : int
        Min number of active stations for event detection
    cull_time : int
        Min time of catalog event
    years : list
        Years data corresponds to
    plot : bool
        Whether to plot the catalog events

    Returns
    -------
    catalog : list
        List of pd.DataFrame catalog events
    """

    picks = Catalog.Picks(data)
    picks.lls_detection(window, slide)
    merged_df = picks.merge()
    sorted_list = picks.on_off_list()
    picks.no_data_csv(sorted_list)

    merged = Catalog.Events(merged_df)
    threshold = merged.pick_events(sorted_list, active_stas=2)
    if plot:
        indices = merged.on_off_indices(sorted_list)
        merged.plot_picking(indices, threshold, num_plots=25)
    catalog = merged.make_catalog(cull_time=30)

    save_dir = f"./{years[0]}_{years[-1]}Events"
    Catalog.save_catalog(catalog, save_dir)

    return catalog
