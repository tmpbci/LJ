Multi Laser planetarium in python3 for LJ.
v0.01
Sam Neurohack

User can define :

- Observer position using GPS coordinates or built in cities catalog on earth.
- Observer time. If you choose Now, the sky is updated live, so you can virtual sky photography :)
- Each laser starchart has a center direction like Azimuth : 63.86° & Altitude: 61.83° and a Field of view like 90°. For the all sky with 4 lasers, give 90° FOV per laser.
- What is displayed : Solar system objects, Stars, Compass letters.
- 

Some future features : 

- Constellations display
- 3D with anaglyph
- Time Speed setting
- What do you want ?

User must understand Right Ascension/Declinaison and Azimuth/Altitude coordinates system. Some needed astronomy concepts online :
https://rhodesmill.org/skyfield/stars.html
https://in-the-sky.org//staratlas.php?ra=15.358411414&dec=73.47660962&limitmag=2
http://www.physics.csbsju.edu/astro/SF/SF.06.html


This project is on "OK" precision grade and definately not coding skills show off, I'm learning python coding it. To check accuracy, one can compare to :
https://www.calsky.com/cs.cgi?cha=7&sec=3&sub=2


The author barely understand astronomy so please report if you find newbie errors sam (at) neurohack cc

This project uses the awesome Skyfield by Brandon Rhodes and Astropy. 

Kernels for Sky objects positions references :
Acton, C.H.; "Ancillary Data Services of NASA's Navigation and Ancillary Information Facility;" Planetary and Space Science, Vol. 44, No. 1, pp. 65-70, 1996.

Charles Acton, Nathaniel Bachman, Boris Semenov, Edward Wright; A look toward the future in the handling of space science mission geometry; Planetary and Space Science (2017);
DOI 10.1016/j.pss.2017.02.013
https://doi.org/10.1016/j.pss.2017.02.013 

