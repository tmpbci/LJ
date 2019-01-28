Le projet planetarium laser style.

Il y a plusieurs idees liees entre elles. En etant tres conservateur disons 150 etoiles par laser, on peut avec 4 lasers affiché 600 etoiles :) zoomer dans une constellation, etc..

On veut, sans connexion internet (donc stocker les infos en local), choisir/afficher les etoiles dans une direction du ciel avec pour origine un lieu sur terre (Paris ?) a telle date/heure. 

Les ressources trouvées pour l'instant qui machent le travail skyfield, jplephem (du meme auteur) 
et le catalogue hipparcos : 
https://rhodesmill.org/skyfield/stars.html
https://in-the-sky.org//staratlas.php?ra=15.358411414&dec=73.47660962&limitmag=2
http://www.physics.csbsju.edu/astro/SF/SF.06.html

En sortie on a besoin d'une liste de coordonnées, ca serait le luxe avec la couleur, la position 3D et la constellation le cas echeant. Pas besoin d'interface graphique on a deja.

N'importe quelle contribution sera grandement utile : recherche, code,... Evidement toutes les personnes qui participent sont creditées dans les auteurs.

Les etoiles ont des positions dans plusieurs reperes, quel est le nom de celui qui nous importe : un endroit sur terre a une date qui peut changer cf skyfield ? Quelle base de données utiliser ? Si c'est bien hipparcos, comment avoir la liste des x etoiles les plus brillantes, comment avoir une liste des constellations classique ? comment les dessiner ? Ursa minor a plein d'etoiles, la liste exhaustive est tres interessante aussi, tout ce qui vous interessera,...

La position 3D est interessante parce qu'on a deja l'algo pour faire de l'anaglyph, vert pour un oeil et rouge pour l'autre et les gens ont souvent une impression de proximité dans une constellation ce qui est tres faux et donc je me vois bien faire une rotation autour d'une constellation pour montrer les distances colossales en Z.

Pour l'instant en python, j'affiche la position des planetes (des points) dans le systeme solaire grace a jplephem tel jour a telle heure.

Il y a donc besoin de jplephem et d'une base pour cet exemple texte :

pip install jplephem
wget http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp

Je peux evidement donner tout le projet avec simulateur de laser si besoin.