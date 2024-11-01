Figure 1 [Figure1.png]

Stations.txt gives approximate station location in Polar Stereographic (PS71).
X and Y coordinates are from the initial line of the first GNSS .pos file for 
that station.

Stations[GZ]Bottom.txt and  Stations[GZ]Top.txt are handcrafted subsections of 
Stations.txt with codes for label placement in GMT. Files with GZ are used for
labeling the inset map, while files without GZ are used to label the main map.
Moa.cpt is a grayscale colorplot used for the Moasic of Antarctica.

To create Figure1.png, run Figure1.sh. Requires the files specified above to be
in the same folder as the shell script and GMT>6 installed.
