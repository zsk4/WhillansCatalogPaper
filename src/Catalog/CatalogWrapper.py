"""
Wrapper for calling several catalog functions at once

Zachary Katz
zachary_katz@mines.edu
August 2024


"""

import Catalog.Catalog as Catalog  # In same folder as this file so no src.Catalog needed


def full_catalog_run(
    data: list, years: list, window: int, slide: int, active_stas: int, cull_time: int
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

    Returns
    -------
    catalog : list
        List of pd.DataFrame catalog events
    """

    picks = Catalog.Picks(data)
    picks.lls_detection(window, slide)
    merged = picks.merge()
    sorted_list = picks.on_off_list()
    picks.no_data_csv(sorted_list)
    indices = picks.on_off_indices(merged, sorted_list)

    merged, threshold = picks.pick_events(merged, sorted_list, active_stas=2)
    picks.plot_picking(merged, indices, threshold, num_plots=4)

    catalog = picks.make_catalog(merged, cull_time=30)
    save_dir = f"./{years[0]}_{years[-1]}Events"
    picks.save_catalog(catalog, save_dir)

    return catalog
