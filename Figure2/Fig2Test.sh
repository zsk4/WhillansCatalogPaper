#!/bin/bash

# Zachary Katz
# 04 August 2024

#Plot Whillans GNSS events and 2nd derivs. Use color to emphasize certain stations.
# Plot overview of my linear least squares residual proccess.

#############################
### CHANGEABLE PARAMETERS ###
out=Figure2TEST #Output file name
plotter=LeastSquaresGMT.txt # Plotting file name
base=-0.05 # Lower Y-extent of plot
top=0.6 # Upper Y-extent of plot
grad_base=-1.3 # Lower Y-extent of 2nd derivative plot [in um/s^2]
grad_top=1.7 # Upper Y-extent of 2nd derivative plot [in um/s^2]
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

# Loop over date directories
for date in ${dir}/* ; do
	if [ -d $date ] ; then
		gmt subplot set 0,${subplot_counter}
		
		subplot_counter=$((subplot_counter + 1))
					# Loop over each station file
		STA_COUNTER=0
		for file in ${date}/*x.txt ; do
			sta=$(awk '{print $2}' $file | head -n 1)
			sta=${sta%X} # Station name without trailing x
			st=$(awk 'NR>1{print $1"T"$2}' $file | head -n 1)
			ed=$(awk 'NR>1{print $1"T"$2}' $file | tail -n 1)
			#st=2013-03-13T02:50:00
			region=${st}T/${ed}T/${base}/${top}
			gmt basemap -R$region -BWS -Bpya0.2f0.1	
			gmt basemap -R$region -Bpya0.2f0.1+l"Station @[\Delta@[X (PS71) [m]" -BWS -Bpxa1Hf10m+l"Time [UTC]"
			
			if in_list "$emph_stas" $sta ; then
				awk 'NR>1{print $1"T"$2, $3}' $file | gmt psxy -R$region -W0.8p,${emph_cols[${STA_COUNTER}]}
				STA_COUNTER=$((STA_COUNTER + 1))
			fi
		done
		
        gmt text -R$region -F+cTL+f16,Helvetica-Bold,33/49/77 -D4c/-4c <<EOF
			precursor
EOF
		echo "2013-03-12T10:10:00 0.15 0 2c" | gmt psxy -R$region -Sv1c+bt+et+n0.1+p2p,"160/56/32"
		echo "2013-03-12T10:40:00 0.12 180 0.5c" | gmt psxy -R$region -Sv1c+et+n0.1+p2p,"160/56/32"
		echo "2013-03-12T10:40:00 0.12 60 0.5c" | gmt psxy -R$region -Sv1c+et+n0.1+p2p,"160/56/32"
	fi

rm legend.txt

done
gmt subplot end
gmt end
