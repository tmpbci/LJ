//
// LJ.js v0.7.1
//

// LJ websocket address. Change here if LJ is not bind to 127.0.0.1

  var LJ = 'ws://127.0.0.1:9001/'

//
// Central horizontal menu
//

	function noMenu() {
		// Set all central menu buttons with normal button style
	  var x = document.getElementById("align");
	    x.value = 0 ;
		var x = document.getElementById("run");
		  x.value = 0 ;
		var x = document.getElementById("simu");
      x.value = 0 ;
		var x = document.getElementById("live");
      x.value = 0 ;

		// Hide all possible main central grids.
		var x = document.getElementById("mgalign");
       	x.style.display = "none";
		var x = document.getElementById("mgsimu");
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
    	var x = document.getElementById("align");
        x.value = 1 ;
    	}

  function showRun() {
      noMenu();
     	var x = document.getElementById("mgrun");
     	   x.style.display = "grid";
     	var x = document.getElementById("run");
       x.value = 1 ;
        	}

  function showCanvas() {
      noMenu();
     	var x = document.getElementById("mgsimu");
        	x.style.display = "grid";
      var x = document.getElementById("cnvbuttons");
         x.style.display = "grid";
     	var x = document.getElementById("simu");
          x.value = 1 ;
        	}

  function showLive() {
    	noMenu();
   	  var x = document.getElementById("mglive");
   	     x.style.display = "grid";
   	  var x = document.getElementById("live");
         x.value = 1 ;
     	}


//
// SimuUIs 
//

  function nosimuUI() {
    // Hide all possible main central grids.
      var x = document.getElementById("planetUI");
        x.style.display = "none";
      var x = document.getElementById("nozoidUI");
        x.style.display = "none";
      var x = document.getElementById("aiUI");
        x.style.display = "none";
      var x = document.getElementById("lissaUI");
        x.style.display = "none";
      var x = document.getElementById("vjUI");
        x.style.display = "none";
      var x = document.getElementById("poseUI");
        x.style.display = "none";
      var x = document.getElementById("wordsUI");
        x.style.display = "none";
      var x = document.getElementById("pluginsUI");
        x.style.display = "none";
    }

  function showplanetUI() {
      nosimuUI();
      var x = document.getElementById("planetUI");
       x.style.display = "grid";
       _WS.send("/planet/ping");
      }

  function shownozoidUI() {
      nosimuUI();
      var x = document.getElementById("nozoidUI");
       x.style.display = "grid";
       _WS.send("/nozoid/ping");
      }

  function showaiUI() {
      nosimuUI();
      var x = document.getElementById("aiUI");
       x.style.display = "grid";
      }

  function showlissaUI() {
      nosimuUI();
      var x = document.getElementById("lissaUI");
       x.style.display = "grid";
      }

  function showvjUI() {
      nosimuUI();
      var x = document.getElementById("vjUI");
       x.style.display = "grid";
       _WS.send("/bank0/ping");
      }


  function showposeUI() {
      nosimuUI();
      var x = document.getElementById("poseUI");
       x.style.display = "grid";
       _WS.send("/pose/ping");
      }


  function showwordsUI() {
      nosimuUI();
      var x = document.getElementById("wordsUI");
       x.style.display = "grid";
       _WS.send("/words/ping");
      }

  function showpluginsUI() {
      nosimuUI();
      var x = document.getElementById("pluginsUI");
       x.style.display = "grid";
       //_WS.send("/words/ping");
      }

//
// Button clicked 
//

  function buttonClicked(clicked_id) {

      _WS.send("/" + clicked_id);

      // update Canvas right part of maingrid 
      if (clicked_id === "planet/planetUI") {
         showplanetUI();
         }
      if (clicked_id === "nozoid/nozoidUI") {
         shownozoidUI();
         }
      if (clicked_id === "ai/aiUI") {
         showaiUI();
         }
      if (clicked_id === "lissa/lissaUI") {
         showlissaUI();
         }
      if (clicked_id === "bank0/vjUI") {
         showvjUI();
         }
      if (clicked_id === "pose/poseUI") {
         showposeUI();
         }
      if (clicked_id === "words/wordsUI") {
         showwordsUI();
         }
      if (clicked_id === "lj/pluginsUI") {
         showpluginsUI();
         }
      if (clicked_id === "nozoid/down 50") {
          var x = document.getElementById("nozoid/down 50");
          x.value = 0 ;
         }
      }


  
//
// Forms submits
//

  function onSubmit(clicked_id) {
    var input = document.getElementById(clicked_id);
    console.log("/" + clicked_id + " " + input.value);
    _WS.send("/" + clicked_id + " " + input.value);
    _WS.showout("/" + clicked_id + " " + input.value);
    }


//
// Websocket handler
//

		var  pl = "";
		var  pl2 = new Array();
    var _WS = {
    uri: LJ,
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
      document.getElementById("on").value = 1;
    },

    onClose: function () {
      _WS.showout('DISCONNECTED');
      document.getElementById("on").value = 0;
      document.getElementById("lstt/0").value = 0;
      document.getElementById("lstt/1").value = 0;
      document.getElementById("lstt/2").value = 0;
      document.getElementById("lstt/3").value = 0;
      document.getElementById("lack/0").value = 0;
      document.getElementById("lack/1").value = 0;
      document.getElementById("lack/2").value = 0;
      document.getElementById("lack/3").value = 0;
    },

    onMessage: function (e) {
      var res = e.data.split(" ");
      //console.log(e.data)
      //console.log(res[0].substring(0,6))
      //console.log(res)
      //console.log(res[0].slice(1))

		  switch (res[0].substring(0,6)) {
    			
          case "/statu":
    				  _WS.showstatus(e.data.slice(8));
        			break;
          case "/simul":
        			pl = e.data.slice(7);
        			pl2 = eval(pl.replace(/[()]/g, ''));
        			break;
        	case "/plpoi":
        			//console.log("plpoint");
        			break;
        	default:
              //console.log(e);
        			document.getElementById(res[0].slice(1)).value = res[1];
              _WS.showin(e.data);
              }
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

