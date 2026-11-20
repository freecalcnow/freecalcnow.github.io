/* FreeCalcNow games — bots + how-to (v8).
   Bots fill every game so matches never feel empty. They have player-like
   names and avatars and play alongside you. There is NO fake "real users
   online" number anywhere: real online multiplayer needs a server, which
   the free static site does not have yet. The panel says so plainly.
   How-to rule (owner, 20 Nov 2026): the how-to panel shows ONLY the first
   time a game is played on this device (localStorage fcn-howto-seen-<slug>).
   Later visits show only a small "How to play" button to reopen it. */
(function () {
  "use strict";
  var NAMES = ["Ayesha", "Bilal", "Zara", "Omar", "Liam", "Sofia", "Arslan", "Mina",
    "Hassan", "Noor", "Ethan", "Mia", "Ali", "Sara", "Danish", "Hina", "Lucas",
    "Emma", "Usman", "Amina", "Noah", "Ava", "Hamza", "Fatima", "Leo", "Ivy",
    "Kabir", "Anaya", "Rayan", "Meera", "Felix", "Nina", "Yusuf", "Layla",
    "Owen", "Ruby", "Imran", "Tara", "Jay", "Elena", "Ravi", "Dina"];
  var COLORS = ["#dc2626", "#ea580c", "#d97706", "#92400E", "#0B1F3A", "#0369A1",
    "#0891b2", "#2563eb", "#4f46e5", "#7c3aed", "#db2777", "#be185d", "#b45309", "#4338ca"];

  function hash(s) { var h = 0; for (var i = 0; i < s.length; i++) { h = (h * 31 + s.charCodeAt(i)) >>> 0; } return h; }
  function rng(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  function initials(name) { var p = name.split(/[\s-]+/); return (p[0][0] + (p[1] ? p[1][0] : "")).toUpperCase(); }
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function read(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  function makeBots(slug, count) {
    var r = rng(hash(slug) * 2654435761 + 97);
    var used = {}, bots = [], i = 0, guard = 0;
    while (bots.length < count && guard++ < 500) {
      var name = NAMES[Math.floor(r() * NAMES.length)];
      if (used[name]) continue;
      used[name] = 1;
      bots.push({ name: name, color: COLORS[Math.floor(r() * COLORS.length)],
        score: Math.floor(r() * 60) + 5, games: Math.floor(r() * 40) + 1 });
      i++;
    }
    return bots;
  }

  function avatar(b, size) {
    return '<span class="fcn-av" style="background:' + b.color + ';width:' + size + 'px;height:' + size + 'px;line-height:' + size + 'px">' + initials(b.name) + '</span>';
  }

  /* Players panel: "You" + 15 bots, scores tick live. mountEl gets the panel. */
  function renderPlayers(mountEl, slug, yourScore) {
    if (!mountEl) return;
    var bots = makeBots(slug, 15);
    var you = { name: "You", color: "#0B1F3A", score: yourScore || 0, games: 1 };
    var all = bots.concat([you]);
    function row(p, rank) {
      return '<li class="fcn-pl-row' + (p.name === "You" ? " fcn-you" : "") + '">' +
        '<span class="fcn-pl-rank">' + rank + '</span>' + avatar(p, 30) +
        '<span class="fcn-pl-name">' + p.name + (p.name === "You" ? " (you)" : "") + '</span>' +
        '<span class="fcn-pl-games">' + p.games + ' games</span>' +
        '<b class="fcn-pl-score">' + p.score + '</b></li>';
    }
    function draw() {
      var sorted = all.slice().sort(function (a, b) { return b.score - a.score; });
      var top = sorted.slice(0, 5);
      var youIdx = sorted.findIndex(function (p) { return p.name === "You"; });
      if (youIdx >= 5) top.push(sorted[youIdx]);
      mountEl.innerHTML =
        '<div class="fcn-pl-head"><b>Players in this match</b><span class="fcn-pl-note">16 players · bots play alongside you</span></div>' +
        '<ul class="fcn-pl-list">' + top.map(function (p) { return row(p, sorted.indexOf(p) + 1); }).join("") + '</ul>' +
        '<p class="fcn-pl-foot">Bot players keep every game lively. Real online multiplayer (playing live with real people) needs a server — it arrives when the site grows.</p>';
    }
    draw();
    var tick = 0;
    setInterval(function () {
      tick++;
      var b = bots[Math.floor(Math.random() * bots.length)];
      b.score += 1 + Math.floor(Math.random() * 3);
      if (tick % 4 === 0) { var b2 = bots[Math.floor(Math.random() * bots.length)]; b2.games += 1; }
      draw();
    }, 2800);
  }

  /* Top-players strip for featured games: top 3 bot names + scores. */
  function renderTopPlayers(mountEl, slug) {
    if (!mountEl) return;
    var bots = makeBots(slug, 15).sort(function (a, b) { return b.score - a.score; }).slice(0, 3);
    mountEl.innerHTML = '<span class="fcn-tp-label">Top players:</span> ' + bots.map(function (b, i) {
      return '<span class="fcn-tp">' + (i + 1) + '. ' + avatar(b, 22) + ' ' + b.name + ' · <b>' + b.score + '</b></span>';
    }).join("");
  }

  /* How-to: show ONLY the first time per game per device. */
  function initHowTo(slug) {
    var key = "fcn-howto-seen-" + slug;
    var panel = document.getElementById("fcn-howto");
    var btn = document.getElementById("fcn-howto-btn");
    if (!panel || !btn) return;
    var seen = read(key);
    if (!seen) {
      panel.hidden = false;
      btn.hidden = true;
      store(key, "1");
    } else {
      panel.hidden = true;
      btn.hidden = false;
    }
    btn.addEventListener("click", function () {
      panel.hidden = !panel.hidden;
      btn.textContent = panel.hidden ? "How to play" : "Hide how to play";
    });
  }

  window.FCNBots = { renderPlayers: renderPlayers, renderTopPlayers: renderTopPlayers, initHowTo: initHowTo };

  document.addEventListener("DOMContentLoaded", function () {
    var tops = document.querySelectorAll("[data-fcn-topplayers]");
    for (var i = 0; i < tops.length; i++) renderTopPlayers(tops[i], tops[i].getAttribute("data-fcn-topplayers"));
    var slug = (document.body && document.body.getAttribute("data-fcn-game")) || "";
    if (!slug) return;
    var mount = document.querySelector("[data-fcn-players]");
    if (mount) {
      var best = 0;
      try { best = parseInt(read("fcn_best_" + slug) || "0") || 0; } catch (e) {}
      renderPlayers(mount, slug, best);
    }
    initHowTo(slug);
  });
})();
