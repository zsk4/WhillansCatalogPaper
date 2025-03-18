# WhillansCatalogPaper

Code used to process GNSS data and create figures in Katz, Siegfried, and Padman, 2025, currently in review. GNSS Data associated with this repository is available to reviewers and will be made public before publication. 
> [!WARNING]  
> This repository is still actively undergoing revisions in preparation for paper publication

## Requirements
[Conda](https://www.anaconda.com/docs/getting-started/miniconda/install)

[Generic Mapping Tools (GMT)](https://docs.generic-mapping-tools.org/dev/install.html)

## Quickstart
1. Set up the included conda environment environment.yml, activate the environment, and add the environment to Jupyter as a kernel.
```bash
conda env create -f environment.yml
conda activate whillanscatalogpaper
python -m ipykernel install --user --name whillanscatalogpaper
```

2. Download the data [Default file names given in brackets]

GNSS
.evt files
DOI Forthcoming

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
> Change the paths in the first cell of the notebook to match your data paths.
> 
> Set user-defined variables in the first cell of the notebook.
4. Follow the instructions in each Figure/Table folder to make the figure or Table
5. Run CatalogComparison.ipynb to perform the comparison to the hand-picked catalog 
from [Siegfried et al., 2016](https://doi.org/10.1002/2016GL067758)
6. Use the CatalogViewer.ipynb utility to view specific events

## Notes
1. GNSS RINEX data and kinematic positions are also available at DOI Forthcoming
2. If you have questions, please leave a GitHub issue or email me.

## Citation
If you use code from this repository, please cite both the publication and the code.
If you use data from this repository, please cite both the publication and the data.
