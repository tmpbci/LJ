//
// LJ.js v0.7.0
//


  
// Web Audio buttons handler


// add a listener for each element.
    var message="";
    var log=[];
    var knobs = document.getElementsByTagName('webaudio-knob');
    for(var i = 0; i < knobs.length; i++){
      knobs[i].addEventListener("input",Dump,false);
      knobs[i].addEventListener("change",Dump,false);
    }
    var sliders = document.getElementsByTagName('webaudio-slider');
    for(var i = 0; i < sliders.length; i++){
      sliders[i].addEventListener("input",Dump,false);
      sliders[i].addEventListener("change",Dump,false);
    }
    var switches = document.getElementsByTagName('webaudio-switch');
    for(var i = 0; i < switches.length; i++) {
        switches[i].addEventListener("change",Dump,false);
    }
// Process button events
function Dump(e) {
var str="";
        str=e.type + " : " + e.target.id + " : " + e.target.value + " ";
        //console.log(str);
        log.unshift(str);
        log.length=1;
        str="";
        for(var i=19;i>=0;--i) {
            if(log[i])
                str+=log[i]+"<br/>";
        }
        var evview=document.getElementById("events");
        evview.innerHTML=str;

    if (e.target.id === "noteon" && e.type ==="input")
    	{
    	console.log("only noteon change are sent not input");
    	}
    else
    	{
    	console.log(e.target.id)
    	_WS.send("/" + e.target.id + " " +  e.target.value);
		}
		
    // for /scale : after a change (knob is released) reset knob value to 0
    if (e.target.id.substring(0,5) === "scale" && e.type === "change") {
    	e.target.value = 0;
    	console.log(e.target.id + "set to 0")
    	_WS.send("/" + e.target.id + " " +  e.target.value);
    	}
    // for /loffset : after a change (knob is released) reset knob value to 0
    if (e.target.id.substring(0,7) === "loffset" && e.type === "change") {
    	e.target.value = 0;
    	console.log(e.target.id + "set to 0")
    	_WS.send("/" + e.target.id + " " +  e.target.value);
    	}
    // for /angle : after a change (knob is released) reset knob value to 0
    if (e.target.id.substring(0,5) === "angle" && e.type === "change") {
    	e.target.value = 0;
    	console.log(e.target.id + "set to 0")
    	_WS.send("/" + e.target.id + " " +  e.target.value);
    	}
}


// Websocket Handler

var  pl = "";
var  pl2 = new Array();
var _WS = {
  uri: 'ws://127.0.0.1:9001/',
  ws: null,

  
  init : function (e) {
    _WS.s = new WebSocket(_WS.uri);
    _WS.s.onopen = function (e) { _WS.onOpen(e); };
    _WS.s.onclose = function (e) { _WS.onClose(e); };
    _WS.s.onmessage = function (e) { _WS.onMessage(e); };
    _WS.s.onerror = function (e) { _WS.onError(e); };
  },
  
  onOpen: function () {
    _WS.showout(_WS.uri);
    _WS.showout('CONNECTED');
  },
  
  onClose: function () {
    _WS.showout('DISCONNECTED');
  },
  
  onMessage: function (e) {
    var res = e.data.split(" ");
    //console.log(e.data)
    switch (res[0].substring(0,6)) {
		case "/statu":
			_WS.showstatus(e.data.slice(8));
  			break;
		case "/plfra":
        	pl = e.data.slice(9);
        	//console.log(pl);
        	pl2 = eval(pl.replace(/[()]/g, ''));
  			//console.log(pl2);
  			break;
  		case "/plpoi":
  			console.log("plpoint");
  			break;
  		case "/clien":
  			console.log("New Client : "+res[1])
  			break
  		default:
  			//console.log(res[0] + " "  + res[1])
  			//console.log(res[1])
  			document.getElementById(res[0].slice(1)).value = res[1];
  			_WS.showin(e.data);
        }
    //_WS.showin(e.data);
  },
  
  onError: function (e) {
    _WS.showin('<span style="color: red;">ERROR:</span> ' + e.data);
  },
  
  showin: function (message) {
      var divtext = document.getElementById('showin');
      divtext.innerHTML="";
      divtext.innerHTML= message.toString();
    },
    
  showout: function (message) {
      var divtext = document.getElementById('showout');
      divtext.innerHTML="";
      divtext.innerHTML= message.toString();
    },
    
  showstatus: function (message) {
      var divtext = document.getElementById('showstatus');
      divtext.innerHTML="";
      divtext.innerHTML= message.toString();
    },
    
  send: function (message) {
    if (!message.length) {
      alert('Empty message not allowed !');
    } else {
      _WS.showout(message);
      _WS.s.send(message);
    }
  },
  
  close: function () {
    _WS.showout('GOODBYE !');
    _WS.s.close();
  }
};

window.addEventListener('load', _WS.init, false);


// Menu Handler

function noMenu() {
	// Set all menu button with normal button style
    var x = document.getElementById("showalign");
    x.className = "button";
    
	var x = document.getElementById("showrun");
	x.className = "button";
	
	var x = document.getElementById("showcanvas");
	x.className = "button";
	
	var x = document.getElementById("showlive");
	x.className = "button";

	// Hide all possible main central grids.
	var x = document.getElementById("mgalign");
    x.style.display = "none";
    
	var x = document.getElementById("mgcanvas");
  	x.style.display = "none";
  	
  	var x = document.getElementById("mgrun");
  	x.style.display = "none";
  	
  	var x = document.getElementById("mglive");
  	x.style.display = "none";
	}

function showAlign() {
	noMenu();
  	var x = document.getElementById("mgalign");
  	x.style.display = "grid";
  	
  	var x = document.getElementById("showalign");
  	x.className = "button:checked";
  	}

function showRun() {
    noMenu();
  	var x = document.getElementById("mgrun");
  	x.style.display = "grid";
  	
  	var x = document.getElementById("showrun");
  	x.className = "button:checked";
    }

function showCanvas() {
   	noMenu();
  	var x = document.getElementById("mgcanvas");
    x.style.display = "block";
    
  	var x = document.getElementById("showcanvas");
  	x.className = "button:checked";
    }

function showLive() {
   	noMenu();
  	var x = document.getElementById("mglive");
  	x.style.display = "grid";
  	
  	var x = document.getElementById("showlive");
  	x.className = "button:checked";
    }

function buttonClicked(clicked_id) {
   	_WS.send("/" + clicked_id);
   	}

function onSubmit(clicked_id) {
    var input = document.getElementById(clicked_id);
    console.log("/" + clicked_id + " " + input.value);
    _WS.send("/" + clicked_id + " " + input.value);
    _WS.showout("/" + clicked_id + " " + input.value);
    }
  