// Send points lists to redis server 
// In compatible LJay string format (pythonic lists)

var redis = require("redis"),
client = redis.createClient(6379,'127.0.0.1');



function rgb2int(r,g,b) {
    // Generate color from r g b components
    var color = hex(r) + hex(g) + hex(b); 
    return parseInt(color, 16)
	}

function hex(v) {
    // Get hexadecimal numbers.
    var hex = v.toString(16);
    if (v < 16) {
        hex = "0" + hex;
    }
    return hex;
}

// add one dot to Laser 0 point list
function adddot0(dotdata){
	var dotstring = "(" + dotdata + "),";
	pl0 += dotstring;
	}

// add one dot to Laser 1 point list
function adddot1(dotdata){
	var dotstring = "(" + dotdata + "),";
	pl1 += dotstring;
	}

// Generate same square to laser 0 and laser 1
function GenPoints() 
	{
	var pt = {};

	// direct colors, i.e red
	pt.r = 255;
	pt.g = 0;
	pt.b = 0;

	// named colors
	var white = rgb2int(255, 255, 255);

	pt.x = 100;
	pt.y = 200;
	adddot0([pt.x, pt.y, rgb2int(pt.r, pt.g, pt.b)]);
	adddot1([pt.x, pt.y, rgb2int(pt.r, pt.g, pt.b)]);
	
	pt.x = 100;
	pt.y = 300;
	adddot0([pt.x, pt.y, white]);
	adddot1([pt.x, pt.y, white]);

	pt.x = 200;
	pt.y = 300;
	adddot0([pt.x, pt.y, white]);
	adddot1([pt.x, pt.y, white]);

	pt.x = 200;
	pt.y = 200;
	adddot0([pt.x, pt.y, white]);
	adddot1([pt.x, pt.y, white]);

	pt.x = 100;
	pt.y = 200;
	adddot0([pt.x, pt.y, white]);
	adddot1([pt.x, pt.y, white]);
	}

// Point lists strings
var pl0 = "[";
var pl1 = "[";
GenPoints();
pl0 = pl0.slice(0,-1) + "]"
pl1 = pl1.slice(0,-1) + "]"

console.log(pl0);
console.log(pl1);

// Send points lists to redis server
client.set("/pl/0",pl0);
client.set("/pl/1",pl1);

// Quit
client.quit()

