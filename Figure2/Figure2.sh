#!/bin/bash

# Zachary Katz
# 04 August 2024

#Plot Whillans GNSS events and 2nd derivs. Use color to emphasize certain stations.
# Plot overview of my linear least squares residual proccess.

#############################
### CHANGEABLE PARAMETERS ###
out=Figure2 #Output file name
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
rm -r $(pwd)/NoData2stas
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
				
		#echo 'N 2' >> legend.txt #One or two column legend
		
		# Loop over each station file
		STA_COUNTER=0
		for file in ${date}/*x.txt ; do
			sta=$(awk '{print $2}' $file | head -n 1)
			sta=${sta%X} # Station name without trailing x
			st=$(awk 'NR>1{print $1"T"$2}' $file | head -n 1)
			ed=$(awk 'NR>1{print $1"T"$2}' $file | tail -n 1)
			#st=2013-03-13T02:50:00
			region=${st}T/${ed}T/${base}/${top}
			gmt basemap -R$region -BW -Bpya0.2f0.1
			
			# Make legend in color if to be emphasized
			if in_list "$emph_stas" $sta ; then
				echo "C ${emph_cols[${STA_COUNTER}]}" >> legend.txt
				echo "S 0.1i - 0.1i - 1.2p,${emph_cols[${STA_COUNTER}]} 0.2i" $sta  >> legend.txt
				echo "C 0" >> legend.txt
				STA_COUNTER=$((STA_COUNTER + 1))
			else
				#echo 'S 0.1i - 0.15i - 1.2p,black 0.3i' $sta >> legend.txt
				awk 'NR>1{print $1"T"$2, $3}' $file | gmt psxy -R$region -Wgray76
			fi
			
		done
		
		# Loop over station files again to plot the emphasized stations in color
		# on top of the other time series
		STA_COUNTER=0
		for file in ${date}/*.txt ; do
			sta=$(awk '{print $2}' $file | head -n 1)
			sta=${sta%X}
			if in_list "$emph_stas" $sta ; then
				awk 'NR>1{print $1"T"$2, $3}' $file | gmt psxy -R$region -W0.8p,${emph_cols[${STA_COUNTER}]}
				STA_COUNTER=$((STA_COUNTER + 1))
			fi
		done

		# Plot 2nd derivative
		file=${date}/grad2.txt
		st=$(awk 'NR>1{print $1"T"$2}' $file | head -n 1)
		ed=$(awk 'NR>1{print $1"T"$2}' $file | tail -n 1)
		pick=$(awk 'NR>1{print $4"T"$5}' $file | head -n 1)
		region_grad=${st}T/${ed}T/${grad_base}/${grad_top}
		gmt basemap -R$region_grad -BE -Bpya0.4f0.2
		awk 'NR>1{print $1"T"$2, $3}' $file | gmt psxy -R$region_grad -W0.8p,135/158/195
		gmt psxy -R$region_grad -W0.8p,135/158/195 <<EOF
		$pick ${grad_top}
		$pick ${grad_base}
EOF
		# Plot legend
		echo "C gray65" >> legend.txt
		echo 'S 0.1i - 0.1i - 1.2p,gray65 0.2i' 'Other Stations' >> legend.txt

		echo "C 135/158/195" >> legend.txt
		echo "G 0.1i " >> legend.txt

		echo 'S 0.1i - 0.1i - 1.2p,135/158/195 0.2i' '@[\Sigma@[ 2nd Derivative' >> legend.txt
		gmt set FONT_ANNOT_PRIMARY 12p
		gmt legend -DjTL+o0.2/0.3+w3.7 legend.txt
		gmt set FONT_ANNOT_PRIMARY 15p
		date=${st%%T*} 
		gmt basemap -R$region -Bpya0.2f0.1+l"Station @[\Delta@[X (PS71) [m]" -BWS -Bpxa1Hf10m+l"Time (${date}) [UTC]"
		gmt basemap -R$region_grad -Bpya0.4f0.2+l"@[\Sigma@[ 2nd Derivative [@[\mu m/s^2@[]" -BE
		
		echo $label | gmt text -R$region -N -F+cTL+f16,Helvetica-Bold,33/49/77 -D0.1c
		label="c."
		
		if [ $subplot_counter -eq 1 ]; then
            gmt text -R$region -F+cTL+f16,Helvetica-Bold,33/49/77 -D0.1c <<EOF
			precursor
EOF
			echo "2013-03-13T02:50:00 0.2 0 2i" | gmt psxy -R$region -Sv1c+bt+et
			echo "2013-03-13T02:50:00 0.2 0 2i 270 360" | gmt psxy -R$region -Sv1c+bt+et
		fi
	fi

rm legend.txt

done
gmt subplot end

# Plot gmt leastsquares residuals on top of the other plots
echo Least Squares
#Get start and end of plot and make region
st=$(awk 'NR>1{print $1"T"$2}' $plotter | head -n 1)
ed=$(awk 'NR>1{print $1"T"$2}' $plotter | tail -n 1)
region_res=$st/$ed/-1/20
region_trace=$st/$ed/-1/5
region_event=$st/$ed/0.5/1.02

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

gmt basemap -R$region_trace -Bpya1f0.5+l"Station @[\Delta@[X (PS71) [m]" -BWS -Bpxa1Df6h+l"Date" -Yh+2.5c -JX26c/10c
gmt set MAP_FRAME_PEN=160/56/32
gmt set MAP_TICK_PEN=160/56/32
gmt set FONT_LABEL=160/56/32
gmt set FONT_ANNOT=160/56/32
gmt basemap -R$region_res -Bpya5f2.5+l"Sliding Least Squares Residual [m]" -BE
gmt set MAP_FRAME_PEN=gray44
gmt set MAP_TICK_PEN=gray44
gmt set FONT_LABEL=gray44
gmt set FONT_ANNOT=gray44
gmt basemap -R$region_trace -Bpya1f0.5+l"Station @[\Delta@[X (PS71) [m]" -BW

echo "Plot Traces"
COL_COUNTER=2
COLOR_COUNTER=1
tr_color=("gray50" "gray60" "gray70" "gray80" "gray90" "gray55" "gray65" "gray75" "gray85" "gray50" "gray60" "gray70" "gray80" "gray90") # Grays for traces
for col in $(awk 'NR==1{print $0}' $plotter); do
	if [[ $col == *x ]] ; then
		echo $col
		awk -v col="$COL_COUNTER" 'NR>1{print $1"T"$2, $col}' $plotter | gmt psxy -R$region_trace -W0.8p,${tr_color[${COLOR_COUNTER}]}
		COLOR_COUNTER=$((COLOR_COUNTER + 1))
	fi
	COL_COUNTER=$((COL_COUNTER + 1))
done

echo "Plot Residuals"
awk 'NR>1{print $1"T"$2, $(NF - 2)}' $plotter | gmt psxy -R$region_res -W1p,160/56/32
awk 'NR>1{print $1"T"$2, $NF}' $plotter | gmt psxy -R$region_res -W1p,237/179/165
awk 'NR>1{print $1"T"$2, $(NF - 1)}' $plotter | gmt psxy -R$region_event -gy0.1 -W4p,33/49/77

gmt text -R$region_res -F+f18,Helvetica,237/179/165 <<EOF
2013-01-26T04:00:00 2 Threshold
EOF

gmt text -R$region_res -F+f18,Helvetica,33/49/77 <<EOF
2013-01-25T06:00:00 18 Events
EOF

echo a. | gmt text -N -R$region_res -F+cTL+f16,Helvetica-Bold,33/49/77 -D0.2c/0.1c

gmt end
