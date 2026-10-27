/* Écran d'accueil minimaliste pour TV Samsung (Tizen). Sans dépendance. */
(function () {
  "use strict";

  var CFG = window.HOME_CONFIG;
  var WALLS = window.HOME_WALLPAPERS || [];
  var hasTizen = typeof window.tizen !== "undefined" && tizen.application;
  var KEY = { LEFT: 37, UP: 38, RIGHT: 39, DOWN: 40, ENTER: 13, BACK: 10009, BACK_PC: 8 };

  var dock = document.getElementById("dock");
  var label = document.getElementById("label");
  var tiles = [];
  var focusIdx = 0;

  // --- Applis --------------------------------------------------------------

  function resolveApps(done) {
    if (!hasTizen) { done({}); return; }
    try {
      tizen.application.getAppsInfo(function (infos) {
        var found = {};
        CFG.apps.forEach(function (app) {
          var hit = infos.filter(function (i) { return app.match.test(i.name) || app.ids.indexOf(i.id) >= 0; })[0];
          if (hit) found[app.name] = { id: hit.id, icon: hit.iconPath };
        });
        done(found);
      }, function () { done({}); });
    } catch (e) { done({}); }
  }

  function buildDock(installed) {
    CFG.apps.forEach(function (app) {
      var el = document.createElement("div");
      el.className = "tile";
      el.setAttribute("role", "listitem");
      el.style.background = app.color;
      var info = installed[app.name];
      if (info && info.icon) {
        var img = new Image();
        img.onerror = function () { el.replaceChild(wordmark(app), img); };
        img.src = info.icon;
        el.appendChild(img);
      } else {
        el.appendChild(wordmark(app));
      }
      if (hasTizen && !info) el.classList.add("missing");
      el.appName = app.name;
      el.appIds = info ? [info.id] : app.ids;
      dock.appendChild(el);
      tiles.push(el);
    });
    setFocus(0);
  }

  function wordmark(app) {
    var s = document.createElement("span");
    s.className = "word";
    s.textContent = app.name;
    s.style.color = app.accent;
    return s;
  }

  function setFocus(i) {
    focusIdx = (i + tiles.length) % tiles.length;
    tiles.forEach(function (t, n) { t.classList.toggle("focus", n === focusIdx); });
    label.textContent = tiles[focusIdx].appName;
  }

  function launch(tile) {
    if (!hasTizen) { toast("Aperçu : ouvrirait " + tile.appName); return; }
    var ids = tile.appIds.slice();
    (function next() {
      var id = ids.shift();
      if (!id) { toast(tile.appName + " n'est pas installée"); return; }
      tizen.application.launch(id, null, next);
    })();
  }

  // --- Fonds d'écran -------------------------------------------------------

  var layers = document.querySelectorAll("#bg .layer");
  var caption = document.getElementById("caption");
  var wallIdx = -1, front = 0;

  function nextWallpaper() {
    if (!WALLS.length) return;
    wallIdx = (wallIdx + 1) % WALLS.length;
    var w = WALLS[wallIdx];
    var img = new Image();
    img.onload = function () {
      var incoming = layers[1 - front], outgoing = layers[front];
      incoming.style.backgroundImage = "url('" + w.file + "')";
      incoming.classList.remove("on");
      void incoming.offsetWidth; // relance l'animation de zoom
      incoming.classList.add("on");
      outgoing.classList.remove("on");
      front = 1 - front;
      caption.textContent = CFG.captions ? w.title : "";
      // précharge le suivant
      var n = WALLS[(wallIdx + 1) % WALLS.length];
      if (n) new Image().src = n.file;
    };
    img.src = w.file;
  }

  // --- Horloge, inactivité, messages ---------------------------------------

  function tick() {
    var d = new Date();
    document.getElementById("clock").textContent =
      ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
    document.getElementById("date").textContent =
      d.toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" });
  }

  var idleTimer;
  function wake() {
    var wasIdle = document.body.classList.contains("idle");
    document.body.classList.remove("idle");
    clearTimeout(idleTimer);
    idleTimer = setTimeout(function () { document.body.classList.add("idle"); }, CFG.idleSeconds * 1000);
    return wasIdle;
  }

  var toastTimer;
  function toast(msg) {
    var t = document.getElementById("toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove("show"); }, 2500);
  }

  // --- Télécommande --------------------------------------------------------

  document.addEventListener("keydown", function (e) {
    if (wake()) { e.preventDefault(); return; } // première touche = sortir du mode contemplation
    switch (e.keyCode) {
      case KEY.LEFT:  setFocus(focusIdx - 1); break;
      case KEY.RIGHT: setFocus(focusIdx + 1); break;
      case KEY.ENTER: launch(tiles[focusIdx]); break;
      case KEY.BACK:
      case KEY.BACK_PC:
        if (hasTizen) tizen.application.getCurrentApplication().exit();
        break;
      default: return;
    }
    e.preventDefault();
  });

  // Quand on revient d'une appli, on réaffiche le dock.
  document.addEventListener("visibilitychange", function () { if (!document.hidden) wake(); });

  // --- Démarrage -----------------------------------------------------------

  tick();
  setInterval(tick, 10000);
  nextWallpaper();
  setInterval(nextWallpaper, CFG.wallpaperSeconds * 1000);
  resolveApps(buildDock);
  wake();
})();
