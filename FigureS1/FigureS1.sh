#!/bin/bash

# Paper Version
# 08 March 2025

#Plot locations of GNSS stations.
#Currently uses Stations.txt, which was created by station_location.ipynb
#Stations.txt has all gps stations, but locations are taken at different years for each.
#Be in conda (gps)

#############################
### CHANGEABLE PARAMETERS ###

out=FigureS1 #Output file name
stations=sta_uptime_input_fixed.txt #Station file name
yannot=Yaxisannot.txt #Annotation file name
xannot=Xaxisannot.txt #Annotation file name
### CHANGEABLE PARAMETERS ###
#############################

region=2007-01-01T/2020-01-01T/0/49

gmt begin
gmt figure $out png A+m0.2c
gmt set FONT_ANNOT_PRIMARY 6p
gmt set FONT_ANNOT_SECONDARY 14p
gmt set FORMAT_TIME_PRIMARY_MAP abbreviated
gmt set FORMAT_DATE_MAP o
gmt set MAP_GRID_PEN_SECONDARY 0.5p,235/239/245
gmt set MAP_FRAME_PEN=33/49/77
gmt set MAP_TICK_PEN=33/49/77
gmt set FONT_LABEL=16p,33/49/77
gmt set FONT_ANNOT=33/49/77

gmt subplot begin 1x1 -Fs20c/10c -M.2c

gmt subplot set 0,0
gmt basemap -R$region -Bpxf3O -Bsx1Y -Bsxg1Y -Bpyc${yannot}+l"Station" -BWS #+t"Station Uptime"
awk 'NR>1{print $2, $4, $1}' $stations | gmt psxy -R$region -SB0.1c+b -G33/49/77

#awk 'NR>1{print $3, $4}' $Stations | gmt text 
gmt subplot end
gmt end
