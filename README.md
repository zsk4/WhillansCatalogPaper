# WhillansCatalogPaper

Code used to process GNSS data and create figures in PAPER NAME. Data associated with this repository is available at DOI. 
> [!CAUTION]  
> This repository is still actively undergoing revisions in preperation for paper publication

# Quickstart
1. Set up the included conda environment whillanscatalogpaper.yml
> [!WARNING]  
> Current yml contains many extraneous dependencies
```bash
conda env create -f environment.yml
```
2. Activate the conda environment
```bash
conda activate whillanscatalogpaper
```
3. Download the data [Default file names given in brackets]
   
GNSS: DOI

Scripps Antarctic Grounding Line: .shp file: [dataset page](https://doi.pangaea.de/10.1594/PANGAEA.819147), [direct download](https://doi.pangaea.de/10013/epic.42133.d001)
[scripps_antarctica_polygons_v1.shp]

MEaSUREs Phase-Based Antarctica Ice Velocity Map, v1: [dataset page](https://nsidc.org/data/NSIDC-0754/versions/1), [direct download](https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0754.001/1996.01.01/antarctic_ice_vel_phase_map_v01.nc)
Then make the velocity magnitude map on the command line following [Siegfried and Fricker 2021](https://github.com/mrsiegfried/Siegfried2021-GRL) Requires Generic Mapping Tools.
```bash
vel = ${path_to_dir}/antarctic_ice_vel_phase_map_v01
gmt grdmath ${vel}?VX 2 POW ${vel}?VY 2 POW ADD SQRT 1000 DIV = ${vel}-vmag.nc
```
[antarctic_ice_vel_phase_map_v01-vmag.nc]

MODIS Mosaic of Antarctica 2009, 750 m, hp1, v1.1, geotiff: [dataset page](https://nsidc.org/data/NSIDC-0593/versions/1), [direct download](https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0593_moa2009/geotiff/moa750_2009_hp1_v01.1.tif.gz)
[moa750_2009_hp1_v1.1.tif]


4. Run the cells in WhillansCatalog.ipynb to make the catalog.
> [!WARNING]  
> Set user-defined variables in first cell
>
> Change the data paths to match your data locations
5. Follow the instructions in each Figure/Table folder to make the figure or Table
6. Run CatalogComparison.ipynb to perform the comparison to the hand-picked catalog 
from [Siegfried et al., 2016](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2016GL067758).
7. Use the CatalogViewer.ipynb utility to view specific events

# Citation
If you use code from this repository, please cite both the publication and the code.
If you use data from this respository, please cite both the publication and the data.
