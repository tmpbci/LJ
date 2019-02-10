Multi Laser planetarium in python3 for LJ.
v0.01
Sam Neurohack


Display all solar planets and hipparcos catalog objects below a given magnitude. Accuracy tested against apparent data and starchart at https://www.calsky.com/cs.cgi?cha=7&sec=3&sub=2

It's an alpha release so a little hardcoded :

- set observer position (find SkyCity, SkyCountryCode) in main.py like 'Paris' and 'FR'
- set observer date.time in InitObserver() arguments (default is now in UTC)
- set what sky part you want to display for each laser in 'LaserSkies' variable : Define alitude and azimuth for top left and bottom right   

It needs more libraries than plan. Currently it relies on the awesome astropy, skyfield,...

Soon some pictures.

To Run :

Launch LJ first
python3 main.py 

For debug options and more type : python3 --help


To install :

go3.sh

NB :
- if you get an year error out of range : install the last skyfield "python-skyfield" in github.  
- Read main.py 







LICENCE : CC
Remember : LJ will automatically warp geometry according to alignement data before sending to lasers. See webUI.  
'''