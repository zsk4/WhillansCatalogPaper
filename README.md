# WhillansCatalogPaper

Code used to process GNSS data and create figures in  

>Katz, Z. S., Siegfried, M. R., & Padman, L. (2026). Slip-event timing and ice velocity vary at long-period ocean tidal frequencies at Whillans Ice Plain, West Antarctica. Journal of Geophysical Research: Earth Surface, 131, e2025JF008770. https://doi.org/10.1029/2025JF008770

## Requirements
[Conda](https://www.anaconda.com/docs/getting-started/miniconda/install)

[Generic Mapping Tools (GMT)](https://docs.generic-mapping-tools.org/dev/install.html)

## Quickstart
1. Set up the included conda environment environment.yml, activate the environment, and add the environment to Jupyter as a kernel. Support for uv forthcoming.
```bash
conda env create -f environment.yml
conda activate whillanscatalogpaper
python -m ipykernel install --user --name whillanscatalogpaper
```

2. Download the data [Default file names given in brackets]

**GNSS**
.pos files \
[dataset_page](https://doi.org/10.5281/zenodo.15412745)
[SSSSJJJ0.pos], where SSSS is the alphanumeric station name (e.g., GZ20) and JJJ is the julian day. Years are given in the files.

**Scripps Antarctic Grounding Line** \
.shp file: \
[dataset page](https://doi.pangaea.de/10.1594/PANGAEA.819147), [direct download](https://doi.pangaea.de/10013/epic.42133.d001) \
[scripps_antarctica_polygons_v1.shp]

**MEaSUREs Phase-Based Antarctica Ice Velocity Map, v1** \
.nc file\
[dataset page](https://nsidc.org/data/NSIDC-0754/versions/1), [direct download](https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0754.001/1996.01.01/antarctic_ice_vel_phase_map_v01.nc) \
Make the velocity magnitude map on the command line following [Siegfried and Fricker 2021](https://github.com/mrsiegfried/Siegfried2021-GRL), where ${path_to_dir} is the path to the directory containing antarctic_ice_vel_phase_map_v01.nc.
```
vel = ${path_to_dir}/antarctic_ice_vel_phase_map_v01
gmt grdmath ${vel}?VX 2 POW ${vel}?VY 2 POW ADD SQRT 1000 DIV = ${vel}-vmag.nc
```
[antarctic_ice_vel_phase_map_v01-vmag.nc]

**MODIS Mosaic of Antarctica 2009, 750 m, hp1, v1.1** \
.tif file \
[dataset page](https://nsidc.org/data/NSIDC-0593/versions/1), [direct download](https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0593_moa2009/geotiff/moa750_2009_hp1_v01.1.tif.gz) \
[moa750_2009_hp1_v1.1.tif]

3. Run the cells in WhillansCatalog.ipynb to make the catalog
> [!IMPORTANT]  
> This step is not required if you are not changing our processing steps and just require the output .evt files, which are available [here](https://doi.org/10.5281/zenodo.15032116).
> Change the paths in the first cell of the notebook to match your data paths.
> 
> Set user-defined variables in the first cell of the notebook.
4. Follow the instructions in each Figure/Table folder to make the figure or Table
5. Run CatalogComparison.ipynb to perform the comparison to the hand-picked catalog 
from [Siegfried et al., 2016](https://doi.org/10.1002/2016GL067758)
6. Use the CatalogViewer.ipynb utility to view specific events

## Notes
1. GNSS RINEX data for stations SLW1, WS04, and WS05 are available at [Zenodo](https://doi.org/10.5281/zenodo.15412745). RINEX data for all other stations is available at [EarthScope](https://www.unavco.org/data/doi/10.7283/YGE1-EF68)
2. Pre-run .evt files made from WhillansCatalog.ipynb, are also available on [Zenodo](https://doi.org/10.5281/zenodo.15032116).
3. If you have questions, please leave a GitHub issue or email me.

## Citation
If you use code from this repository, please cite both the publication and the code.
If you use data from the linked [Zenodo](https://doi.org/10.5281/zenodo.15032116) repository, please cite both the publication and the data.

Publication
>Katz, Z. S., Siegfried, M. R., & Padman, L. (2026). Slip-event timing and ice velocity vary at long-period ocean tidal frequencies at Whillans Ice Plain, West Antarctica. Journal of Geophysical Research: Earth Surface, 131, e2025JF008770. https://doi.org/10.1029/2025JF008770

Data [RINEX For all stations except SLW1, WS04, and WS05]
>Siegfried, M. R., Katz, Z. S., Fricker, H. A., Tulaczyk, S., & Oleszko, M. (2025). WISSARD-SALSA Whillans-Mercer GNSS Network [GPS/GNSS Observations (Aggregation of Multiple Datasets)]. The NSF GAGE Facility operated by EarthScope Consortium. https://doi.org/10.7283/YGE1-EF68

Data [RINEX for SLW1, WSO4, WS05, Reprocessed Kinematic Positions for all Stations, Event Catalog]
>Katz, Z. S., & Siegfried, M. R. (2025). Whillans Ice Plain GNSS RINEX, Kinematic Positions, and Stick-Slip Event Catalog (1.2) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17797751

Code
>Katz, Z. S. (2025). zsk4/WhillansCatalogPaper: Revision2-1 (v1.2.1). Zenodo. https://doi.org/10.5281/zenodo.17958133

