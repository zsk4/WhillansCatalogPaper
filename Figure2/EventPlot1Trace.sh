#!/bin/bash

# Zachary Katz
# 04 August 2024

#Plot Whillans GNSS events and 2nd derivs. Use color to emphasize certain stations.
# Plot overview of my linear least squares residual proccess.

#############################
### CHANGEABLE PARAMETERS ###
out=GPGN573Presentation #Output file name
plotter=LeastSquaresGMT.txt # Plotting file name
base=-0.05 # Lower Y-extent of plot
top=0.6 # Upper Y-extent of plot
grad_base=-1.5 # Lower Y-extent of 2nd derivative plot [in um/s^2]
grad_top=1.5 # Upper Y-extent of 2nd derivative plot [in um/s^2]
emph_stas="GZ15 LA08" # List of stations to show in color
# Colors from http://vrl.cs.brown.edu/color 
emph_cols=("160/56/32" "33/49/77") # Colors corresponding to above stations
### CHANGEABLE PARAMETERS ###


function in_list() {
# Determines if value $2 is in list $1
# Ex. in_list "gz05 gz06 gz07" "gz05" returns 0 (True)
# Ex. in_list "gz05 gz06 gz07" "gz08" returns 1 (False)
	LIST=$1
	VALUE=$2
	for x in $LIST; do
		if [ $x == $VALUE ]; then
			return 0
		fi
	done
	return 1
}

dir=$(pwd)
subplot_counter=0
label="b."

gmt begin
gmt figure $out png A+m0.2c
gmt set FONT_ANNOT_PRIMARY 15p
gmt set FONT_ANNOT_SECONDARY 20p
gmt set FONT_LABEL 16p
gmt set FORMAT_TIME_MAP abbreviated
gmt set FORMAT_DATE_MAP yyyy-mm-dd
gmt set FORMAT_CLOCK_MAP hh:mm
gmt set MAP_FRAME_PEN=33/49/77
gmt set MAP_TICK_PEN=33/49/77
gmt set FONT_LABEL=33/49/77
gmt set FONT_ANNOT=33/49/77
gmt subplot begin 1x2 -Ff26c/7c -M2c 

# Plot gmt leastsquares residuals on top of the other plots
echo Least Squares
#Get start and end of plot and make region
st=$(awk 'NR>1{print $1"T"$2}' $plotter | head -n 1)
ed=$(awk 'NR>1{print $1"T"$2}' $plotter | tail -n 1)
region_res=$st/$ed/-1/20
region_trace=$st/$ed/-0.5/4
region_event=$st/$ed/0.5/1.02

gmt set FONT_LABEL 16p
gmt set FONT_ANNOT_PRIMARY 16p
gmt set FONT_ANNOT_SECONDARY 20p
gmt set FORMAT_TIME_PRIMARY_MAP abbreviated
gmt set FORMAT_DATE_MAP yyyy-mm-dd
gmt set MAP_GRID_PEN_SECONDARY 0.5p,0/0/0
gmt set MAP_FRAME_PEN=0/0/0
gmt set MAP_TICK_PEN=0/0/0
gmt set FONT_LABEL=0/0/0
gmt set FONT_ANNOT=0/0/0

gmt basemap -R$region_trace -Bpya1f0.5+l"Station @[\Delta@[X (PS71) [m]" -BWS -Bpxa1Df6h+l"Date" -Yh+2.5c -JX26c/10c
gmt set MAP_FRAME_PEN=0/0/0
gmt set MAP_TICK_PEN=0/0/0
gmt set FONT_LABEL=0/0/0
gmt set FONT_ANNOT=0/0/0
gmt set MAP_FRAME_PEN=black
gmt set MAP_TICK_PEN=black
gmt set FONT_LABEL=black
gmt set FONT_ANNOT=black
gmt basemap -R$region_trace -Bpya1f0.5+l"Station @[\Delta@[X (PS71) [m]" -BWS -Bpxa2Df12h+l"Date"

echo "Plot Traces"
COL_COUNTER=2
COLOR_COUNTER=1
tr_color=("black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black" "black") # Grays for traces
for col in $(awk 'NR==1{print $0}' $plotter); do
	if [[ $col == gz01x ]] ; then
		echo $col
		awk -v col="$COL_COUNTER" 'NR>1{print $1"T"$2, $col}' $plotter | gmt psxy -R$region_trace -W0.8p,${tr_color[${COLOR_COUNTER}]}
		COLOR_COUNTER=$((COLOR_COUNTER + 1))
	fi
	COL_COUNTER=$((COL_COUNTER + 1))
done
gmt subplot end
gmt end
