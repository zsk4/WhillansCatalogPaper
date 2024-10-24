#!/bin/bash

# Plot overview of my linear least squares residual proccess.

#############################
### CHANGEABLE PARAMETERS ###
out=LeastSquaresGMT #Output file name
plotter=LeastSquaresGMT.txt #Plotting file name. Made by PickEvents.ipynb
### CHANGEABLE PARAMETERS ###
#############################

#Get start and end of plot and make region
st=$(awk 'NR>1{print $1"T"$2}' $plotter | head -n 1)
ed=$(awk 'NR>1{print $1"T"$2}' $plotter | tail -n 1)
region_res=$st/$ed/-1/50
region_trace=$st/$ed/-1/5
region_event=$st/$ed/0.5/1.02

gmt begin
gmt figure $out png A+m0.2c
gmt set FONT_LABEL 16p
gmt set FONT_ANNOT_PRIMARY 16p
gmt set FONT_ANNOT_SECONDARY 20p
gmt set FORMAT_TIME_PRIMARY_MAP abbreviated
gmt set FORMAT_DATE_MAP yyyy-mm-dd
gmt set MAP_GRID_PEN_SECONDARY 0.5p,235/239/245
gmt set MAP_FRAME_PEN=33/49/77
gmt set MAP_TICK_PEN=33/49/77
gmt set FONT_LABEL=33/49/77
gmt set FONT_ANNOT=33/49/77

gmt subplot begin 1x1 -Fs20c/10c -M.2c

gmt subplot set 0,0
gmt basemap -R$region_trace -Bpya1f0.5+l"Station @[\Delta@[X (PS71) [m]" -BWS -Bpxa1Df6h+l"Date"
gmt set MAP_FRAME_PEN=160/56/32
gmt set MAP_TICK_PEN=160/56/32
gmt set FONT_LABEL=160/56/32
gmt set FONT_ANNOT=160/56/32
gmt basemap -R$region_res -Bpya10f5+l"Sliding Least Squares Residual [m]" -BE
gmt set MAP_FRAME_PEN=gray44
gmt set MAP_TICK_PEN=gray44
gmt set FONT_LABEL=gray44
gmt set FONT_ANNOT=gray44
gmt basemap -R$region_trace -Bpya1f0.5+l"Station @[\Delta@[X (PS71) [m]" -BW

echo "Plot Traces"
COL_COUNTER=1
tr_color=("gray50" "gray60" "gray70" "gray80" "gray90" "gray55" "gray65" "gray75" "gray85" "gray50" "gray60" "gray70" "gray80" "gray90") # Grays for traces
for col in $(awk 'NR==1{print $0}' $plotter); do
	if [[ $col == *x ]] ; then
		echo $col
		awk -v col="$COL_COUNTER" 'NR>1{print $1"T"$2, $col}' $plotter | gmt psxy -R$region_trace -W0.8p,${tr_color[${COL_COUNTER}]}
	fi
	COL_COUNTER=$((COL_COUNTER + 1))
done

echo "Plot Residuals"
awk 'NR>1{print $1"T"$2, $14}' $plotter | gmt psxy -R$region_res -W1p,160/56/32
awk 'NR>1{print $1"T"$2, $15}' $plotter | gmt psxy -R$region_res -W1p,237/179/165
awk 'NR>1{print $1"T"$2, $16}' $plotter | gmt psxy -R$region_event -gy0.1 -W4p,33/49/77

gmt text -R$region_res -F+f18,Helvetica,237/179/165 <<EOF
2013-01-26T04:00:00 7.6 Threshold
EOF

gmt text -R$region_res -F+f18,Helvetica,33/49/77 <<EOF
2013-01-25T06:00:00 45 Events
EOF

gmt subplot end
gmt end
