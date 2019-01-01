//
// LJ.js v0.7.0
//



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

