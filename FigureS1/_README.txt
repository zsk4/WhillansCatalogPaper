Figure S1 [FigureS1.png]

08 March 2025
Paper Version

Requirements
Xaxisannot.txt
Yaxisannot.txt


Run StationUptimeInput.ipynb to create
sta_uptime_input.txt

Copy and create fixed version with sed command
> cp sta_uptime_input.txt sta_uptime_input_fixed.txt
> sed -i -E 's/la02\t2/TEMP/g; s/la09\t9/la02\t2/g; s/TEMP/la09\t9/g' sta_uptime_input_fixed.txt

Run FigureS1.sh to create FigureS1.png
