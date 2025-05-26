Zachary Katz
zachary_katz@mines.edu
These event files are meant to be read by figure creation scripts and the event
viewer Jupyter Notebook at https://github.com/zsk4/WhillansCatalogPaper.

Each year folder contains m .evt files which are tab delimited text files, where
m is the number of events in that year.
.evt files contain the following columns
index, date, time,
n columns of the form {sta}x, {sta}y, {sta}z {sta}res, {sta}res_avg, where n is the 
number of operational stations for this event,
sum_res_avg, ressum, event

index - index of each row in the combined dataframe, used to sequence data
date - date of measurement as yyyy-mm-dd
time - time of measurement as hh:mm:ss
{sta}x - x position in PS71 of station [m]
{sta}y - y position in PS71 of station [m]
{sta}z - z position of station [m]
{sta}res - station residual for q min window around this point, where q was
defined when the catalog was made.
{sta}res_avg - avg station residual for the whole year the station was operational
sum_res_avg - sum of all {sta}res_avg entries in a row
ressum - sum of all {sta}res entries in a row
event - Always 1.0, indicating that these rows correspond to an event
