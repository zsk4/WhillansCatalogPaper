#gmt movie main.sh -Sbpre.sh -Chd -Ttimes.txt -Vi -D100 -Zs -Nanim01 -Fmp4 -Pd+ac0+jBC+p5,white+P7,black+w8c --FORMAT_CLOCK_MAP=- --FORMAT_DATE_MAP=yyyy-mm-dd

gmt begin
gmt set MAP_FRAME_TYPE inside
gmt set MAP_FRAME_PEN faint,black@100 # @100 sets transparency to 100

#############################
### CHANGEABLE PARAMETERS ###
stations=../Stations.txt #Station file name
stationsTop=../StationsTop.txt
stationsBottom=../StationsBottom.txt
stationsGZTop=../StationsGZTop.txt
stationsGZBottom=../StationsGZBottom.txt

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

#Figure height (mm)
figheight=115
figheightcm=11.5

#Set figure width and projection based on figheight and region chosen
figwidth=$(gmt math -Q ${xh} ${xl} SUB ${yh} ${yl} SUB DIV ${figheight} MUL = )
figwidthcm=$(gmt math -Q ${figwidth} 10 DIV = ) 
ratio=$(gmt math -Q ${yh} ${yl} SUB ${figheight} 1000 DIV DIV = )
projection=x1:${ratio}
llprojection=s0/-90/-71/1:${ratio} #Why -71 for max distance from projection center?
mapsize=${figwidth}/${figheight}
region=${xl}/${xh}/${yl}/${yh}

gmt subplot begin 1x1 -Fs${mapsize} -Blrbt -Xf0.5c -Y1.5c #-Cw0.5c


gmt events sta_uptime_plot.txt --TIME_UNIT=d -Lt -T${MOVIE_COL0} -R$region -J$projection -G255 -Si0.2c -W0.2p,black

gmt subplot end



#Subplot
#Groudning zone inset map
mxl=-185000
myl=-618000
mxh=-152000
myh=-580000

mfigheight=55
mfigheightcm=5.5
mfigwidth=$(gmt math -Q ${mxh} ${mxl} SUB ${myh} ${myl} SUB DIV ${mfigheight} MUL = )
mfigwidthcm=$( gmt math -Q ${mfigwidth} 10 DIV = )
mratio=$(gmt math -Q ${myh} ${myl} SUB ${mfigheight} 1000 DIV DIV = )
mprojection=x1:${mratio}
mmapsize=${mfigwidth}/${mfigheight}
mgz=${mxl}/${myl}/${mxh}/${myh}

margin=0.5
plotsize=$( gmt math -Q ${figheight} 10 DIV 2 DIV ${margin} SUB = )
xoff=$( gmt math -Q ${figwidthcm} 0.5 SUB = )

#To allign with preflight background, need to manually add -C command from subplot into -X and -Y of subplot...
gmt subplot begin 1x1 -Ff${mfigwidthcm}c/${mfigheightcm}c -M${margin}c -Xf${xoff} -Yf0.5c -Blrbt #-C0.5c

gmt events sta_uptime_plot.txt --TIME_UNIT=d -Lt -T${MOVIE_COL0} -R$mgz+r -J$mprojection -G255 -Si0.2c -W0.2p,black 

gmt subplot end
gmt end
