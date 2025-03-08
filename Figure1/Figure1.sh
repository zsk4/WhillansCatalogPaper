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
out=Figure1 #Output file name
stations=Stations.txt #Station file name
stationsTop=StationsTop.txt
stationsBottom=StationsBottom.txt
stationsGZTop=StationsGZTop.txt
stationsGZBottom=StationsGZBottom.txt
stationsGZ15=GZ15.txt
stationsLA08=LA08.txt

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
background=/mnt/c/Users/ZacharyKatz/Desktop/Research/Background #Folder with grids
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
gmt set MAP_FRAME_PEN=thinner,33/49/77
gmt set MAP_TICK_PEN=33/49/77
gmt set FONT_LABEL=33/49/77
gmt set FONT_ANNOT=33/49/77

gmt figure $out png A+m0.2c

gmt subplot begin 1x1 -Fs${mapsize} -Cw0.5c

#Mosaic of Antarctica
echo Background Mosaic of Antarctica
gmt makecpt -Cgray -T15000/17000/1 -Z
gmt grdimage $moa -R$region -J$projection -C -Bnwse -Bxa25000 -Bya25000 --MAP_FRAME_TYPE=inside --MAP_TICK_LENGTH_PRIMARY=4p \
--MAP_TICK_PEN_PRIMARY=thin

# LAKES HERE #
# Lakes, from https://github.com/mrsiegfried/Siegfried2021-GRL/blob/main/figures/fig1-map/plotSiegfried2021map.sh
echo 'plotting lake outlines - this takes a bit'
h5ls ${lakes} | grep "Group" | awk '{print $1}' > groups
while read g
do
	echo $g
    # dump x and y values to separate files
    h5dump -d /${g}/x -y -A 0 -b LE -o tmpx.bin -O ${lakes}
    h5dump -d /${g}/y -y -A 0 -b LE -o tmpy.bin -O ${lakes}
    gmt convert -bi1 tmpx.bin | tr 'NaN' '>' > tmpx.txt # turn nan separated to > separated
    gmt convert -bi1 tmpy.bin > tmpy.txt
    paste tmpx.txt tmpy.txt > lake.xy
    
    gmt psxy lake.xy -R$region -J$projection -Wthick,black -Gcornflowerblue
    rm lake.xy tmpx.txt tmpy.txt tmpx.bin tmpy.bin
done < groups
rm groups
printf "\ndone plotting lake outlines\n"

#Lat/Long lines
gmt basemap -J$llprojection -R$region -Bxa10g10 -Bya1g1 -BWENS \
--MAP_FRAME_TYPE=inside --FONT_ANNOT_PRIMARY=10p,gray95 \
--MAP_TICK_PEN_PRIMARY=thinner,grey --FORMAT_GEO_MAP=dddF --MAP_POLAR_CAP=90/90 \
--MAP_TICK_LENGTH_PRIMARY=-10p --MAP_ANNOT_OBLIQUE=0 --MAP_ANNOT_OFFSET_PRIMARY=-2p \
--MAP_GRID_PEN_PRIMARY=thinner,grey

#Ice Velocity
echo Ice Velocity
gmt makecpt -Coslo -T0/500/1 #--COLOR_FOREGROUND=240/249/33 --COLOR_BACKGROUND=13/8/135 
gmt grdimage $vel -R$region -J$projection -t40 -C 
gmt grdvector $vx $vy -R$region -J$projection -Ix24 -Q0.2c+e@50 -Ggray@50 -W1p,gray@50 -S0.8c #-S2c

#Grounding Line
echo Grounding Line
gmt psxy $gl -R$region -J$projection -W0.5p,gray90

#Colorbar for ice velocity
barwidth=`gmt math -Q ${figwidth} 10 DIV 0.28 MUL = `
#First with transparent background
gmt colorbar -C -R$region -J$projection -DjTR+w${barwidth}c+jTR+o1c/0.75c+h+ml \
-Bxa250f50+l"Ice Velocity [m a@+-1@+]" -F+gblack+p0.5p,black+c3p -t50 --FONT_ANNOT_PRIMARY=20p,white \
--FONT_LABEL=20p,white --MAP_ANNOT_OFFSET_PRIMARY=4p --MAP_TICK_PEN_PRIMARY=1.5p,white \
--MAP_TICK_LENGTH_PRIMARY=5p --MAP_FRAME_PEN=1.5p,white --MAP_LABEL_OFFSET=8p
#Again without background but not transparent
gmt colorbar -C -R$region -J$projection -DjTR+w${barwidth}c+jTR+o1c/0.75c+h+ml \
-Bxa250f50+l"Ice Velocity [m a@+-1@+]" --FONT_ANNOT_PRIMARY=20p,white \
--FONT_LABEL=20p,white --MAP_ANNOT_OFFSET_PRIMARY=4p --MAP_TICK_PEN_PRIMARY=1.5p,white \
--MAP_TICK_LENGTH_PRIMARY=5p --MAP_FRAME_PEN=1.5p,white --MAP_LABEL_OFFSET=8p

#Scale Bar
echo Scale Bar
len=20000
xset=3250 #Approx allignment with locator map
yset=31500
x1=` gmt math -Q ${xl} $xset ADD = `
x2=` gmt math -Q ${x1} $len ADD = `
y1=` gmt math -Q ${yset} $yl ADD = `
gmt psxy -R$region -J$projection -W3p,"white" <<EOF
${x1} ${y1}
${x2} ${y1}
EOF
gmt text -R$region -J$projection -F+jBL+f10,Helvetica,white -D0c/0.1c <<EOF
${x1} ${y1} 20 km
EOF


#Stations and Labels
#echo Stations and Labels
awk 'NR>1{print $1, $2}' ${stations} | gmt psxy -R$region -J$projection -Si0.3c -G255 -W0.2p,black
awk 'NR>1{print $1, $2}' ${stationsLA08} | gmt psxy -R$region -J$projection -Si0.3c -G33/49/77 -W0.2p,black
awk 'NR>1{print $1, $2}' ${stationsGZ15} | gmt psxy -R$region -J$projection -Si0.3c -G160/56/32 -W0.2p,black
awk 'NR>1{print $1, $2, $3, $4}' ${stationsTop} | gmt pstext -J$projection -F+j+f6p,Helvetica-Bold,white -D0c/0.25c 
awk 'NR>1{print $1, $2, $3, $4}' ${stationsBottom} | gmt pstext -J$projection -F+j+f6p,Helvetica-Bold,white -D0c/-0.25c 

# GL Label
gmt text -R$region -J$projection -F+a310+f9p,Helvetica,white <<EOF
-200000 -535000 Grounding Line
EOF

# Antarctica Locator Map
echo Locator Map
#rossRegion=-2900000/-2900000/2900000/2900000+r #All of antarctica
rossRegion=-760000/-1400000/600000/-350000+r #Ross

rxl=-760000
ryl=-1400000
rxh=600000
ryh=-350000

rfigheight=20
rfigheightcm=2
rfigwidth=`gmt math -Q ${rxh} ${rxl} SUB ${ryh} ${ryl} SUB DIV ${rfigheight} MUL = `
rfigwidthcm=` gmt math -Q ${rfigwidth} 10 DIV = ` 
rratio=`gmt math -Q ${ryh} ${ryl} SUB ${rfigheight} 1000 DIV DIV = `
rossProj=x1:${rratio}
rmapsize=${rfigwidth}/${rfigheight}
rossRegion=${rxl}/${ryl}/${rxh}/${ryh}

gmt inset begin -DjBL+o0.25c/0.25c -R$region -J$projection
gmt psxy ${moa_coast} -R${rossRegion}+r -J${rossProj} -G"white"
gmt psxy ${moa_gl} -R${rossRegion}+r -J${rossProj} -G"gray"
gmt psxy -R${rossRegion}+r -J${rossProj} -W1p,"black" <<EOF
${xl} ${yl}
${xl} ${yh}
${xh} ${yh}
${xh} ${yl}
${xl} ${yl}
EOF

gmt text -R${rossRegion}+r -J${rossProj} -F+f6,Helvetica,black <<EOF
-100000 -900000 Ross
-100000 -1000000 Ice Shelf
EOF
gmt inset end

gmt psxy -R${region} -J${projection} -Wthinner,33/49/77 <<EOF
${mxl} ${myl}
${mxl} ${myh}
${mxh} ${myh}
${mxh} ${myl}
${mxl} ${myl}
EOF

gmt subplot end

#Groudning zone inset map
echo Grounding Zone Insets

margin=0.5
plotsize=` gmt math -Q ${figheight} 10 DIV 2 DIV ${margin} SUB = `
xoff=` gmt math -Q ${figwidthcm} 0.5 SUB = `

gmt subplot begin 1x1 -Ff${mfigwidthcm}c/${mfigheightcm}c -M${margin}c -C0.5c -Xf${xoff}
#gmt makecpt -Cgray -T15000/17000/1 -Z > moa.cpt #Not sure why this fails - use premade colorplot
gmt grdimage $moa -R$mgz+r -J$mprojection -Cmoa.cpt -Blrbt
gmt makecpt -Coslo -T0/500/1 #--COLOR_FOREGROUND=240/249/33 --COLOR_BACKGROUND=13/8/135 
gmt grdimage $vel -J${mprojection} -R$mgz+r -t40 -C -Blrbt
gmt grdvector $vx $vy -R$mgz+r -J${mprojection} -Ix15 -Q0.2c+e@50 -Ggray@50 -W1p,gray@50  -S0.8c #-S2c
gmt psxy $gl -J${mprojection} -R$mgz+r -W0.5p,gray90 -Blrbt

awk 'NR>1{print $1, $2}' ${stations} | gmt psxy -J${mprojection} -R$mgz+r -Si0.3c -G255 -W0.2p,black -Blrbt
awk 'NR>1{print $1, $2}' ${stationsGZ15} | gmt psxy -J${mprojection} -R$mgz+r -Si0.3c -G160/56/32 -W0.2p,black -Blrbt
awk 'NR>1{print $1, $2, $3, $4}' ${stationsGZTop} | gmt pstext -J$mprojection -D0c/0.3c -F+j+f7p,Helvetica-Bold,white
awk 'NR>1{print $1, $2, $3, $4}' ${stationsGZBottom} | gmt pstext -J$mprojection -D0c/-0.3c -F+j+f7p,Helvetica-Bold,white

#Scale Bar
echo Scale Bar
len=10000
xset=1000
yset=1000
x1=` gmt math -Q ${mxl} $xset ADD = `
x2=` gmt math -Q ${mxl} $len ADD = `
y1=` gmt math -Q ${yset} $myl ADD = `
gmt psxy -J${mprojection} -R$mgz+r -W3p,"white" <<EOF
${x1} ${y1}
${x2} ${y1}
EOF
gmt text -J${mprojection} -R$mgz+r -F+jBL+f10,Helvetica,white -D0c/0.1c <<EOF
${x1} ${y1} 10 km
EOF

gmt subplot end

gmt end
