#!/bin/bash

#Plot locations of GNSS stations.
#Currently uses Stations.txt, which was created by station_location.ipynb
#Stations.txt has all gps stations, but locations are taken at different years for each.
#Be in conda (gps)

#TODO Write function to compute figwidth so not repeated as figwidth and mfigwidth

#Adapted from Pygmt scripts on Matthew Siegfried's Github
#SiegVent2023-Geology/figures/plot_siegvent2023_fig1.ipynb
#Siegfried2021-GRL/figures/fig1-map/plotSiegfried2021map.sh

#############################
### CHANGEABLE PARAMETERS ###
out=Figure1TEST #Output file name
stations=Stations.txt #Station file name
stationsTop=StationsTop.txt
stationsBottom=StationsBottom.txt
stationsGZTop=StationsGZTop.txt
stationsGZBottom=StationsGZBottom.txt

#Set region in PS71=3031
xl=-310000
yl=-621000
xh=-140000
yh=-490000

#Figure height (mm)
figheight=100
figheightcm=10
### CHANGEABLE PARAMETERS ###
#############################
mxl=-185000
myl=-618000
mxh=-152000
myh=-580000

mfigheight=55
mfigheightcm=5.5
mfigwidth=`gmt math -Q ${mxh} ${mxl} SUB ${myh} ${myl} SUB DIV ${mfigheight} MUL = `
mfigwidthcm=` gmt math -Q ${mfigwidth} 10 DIV = ` 
mratio=`gmt math -Q ${myh} ${myl} SUB ${mfigheight} 1000 DIV DIV = `
mprojection=x1:${mratio}
mmapsize=${mfigwidth}/${mfigheight}
mgz=${mxl}/${myl}/${mxh}/${myh}

#Set figure width and projection based on figheight and region chosen
figwidth=`gmt math -Q ${xh} ${xl} SUB ${yh} ${yl} SUB DIV ${figheight} MUL = `
figwidthcm=` gmt math -Q ${figwidth} 10 DIV = ` 
ratio=`gmt math -Q ${yh} ${yl} SUB ${figheight} 1000 DIV DIV = `
projection=x1:${ratio}
llprojection=s0/-90/-71/1:${ratio} #Why -71 for max distance from projection center?
mapsize=${figwidth}/${figheight}
region=${xl}/${xh}/${yl}/${yh}

#Load grids
background=/mnt/d/Background #Folder with grids
moa=${background}/moa750_2009_hp1_v1.1.tif #Mosaic of Antarctica
gl=${background}/Antarctica_masks/scripps_antarctica_polygons_v1.shp #Grounding Line
lakes=${background}/SiegfriedFricker2018-outlines.h5 #SiegfriedFricker2018-outlines

#https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0593_moa2009_v02/coastlines/
moa_coast=${background}/moa_2009_coastline_v02.0.gmt
moa_gl=${background}/moa_2009_groundingline_v02.0.gmt

#Magnitude of velocity map made at the command line following Siegfried and Fricker 2021
# > vel = ${background}/antarctic_ice_vel_phase_map_v01
# > gmt grdmath ${vel}?VX 2 POW ${vel}?VY 2 POW ADD SQRT 1000 DIV = ${vel}-vmag.nc
# > gmt grdmath ${vel}?VX 1000 DIV = ${vel}-VX.nc
# > gmt grdmath ${vel}?VX 1000 DIV = ${vel}-VY.nc
vel=${background}/antarctic_ice_vel_phase_map_v01-vmag.nc #Velocity field
vx=${background}/antarctic_ice_vel_phase_map_v01-VX.nc
vy=${background}/antarctic_ice_vel_phase_map_v01-VY.nc

# Normalized arrows
#vx=${background}/antarctic_ice_vel_phase_map_v01.nc-VXnorm.nc
#vy=${background}/antarctic_ice_vel_phase_map_v01.nc-VYnorm.nc

### BEGIN PLOTTING ###
gmt begin
gmt set MAP_FRAME_TYPE plain
#gmt set MAP_FRAME_PEN thinner,black
gmt set MAP_FRAME_PEN=thinner,33/49/77
gmt set MAP_TICK_PEN=33/49/77
gmt set FONT_LABEL=33/49/77
gmt set FONT_ANNOT=33/49/77

gmt figure $out png A+m0.2c

gmt subplot begin 1x1 -Fs${mapsize} -Cw0.5c

#Ice Velocity
echo Ice Velocity
gmt makecpt -Coslo -T0/500/1 #--COLOR_FOREGROUND=240/249/33 --COLOR_BACKGROUND=13/8/135 
gmt grdimage $vel -R$region -J$projection -t40 -C 
gmt grdvector $vx $vy -R$region -J$projection -Ix25 -Q0.2c+e@50 -Ggray@50 -W1p,gray@50  -S0.8c

gmt subplot end
#Groudning zone inset map
echo Grounding Zone Insets

margin=0.5
plotsize=` gmt math -Q ${figheight} 10 DIV 2 DIV ${margin} SUB = `
xoff=` gmt math -Q ${figwidthcm} 0.5 SUB = `

gmt subplot begin 1x1 -Ff${mfigwidthcm}c/${mfigheightcm}c -M${margin}c -C0.5c -Xf${xoff}
#gmt makecpt -Cgray -T15000/17000/1 -Z > moa.cpt #Not sure why this fails - use premade colorplot
gmt makecpt -Coslo -T0/500/1 #--COLOR_FOREGROUND=240/249/33 --COLOR_BACKGROUND=13/8/135 
gmt grdimage $vel -J${mprojection} -R$mgz+r -t40 -C -Blrbt
gmt grdvector $vx $vy -R$mgz+r -J${mprojection} -Ix25 -Q0.2c+e@50 -Ggray@50 -W1p,gray@50  -S2c

gmt subplot end


gmt end
