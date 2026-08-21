/* ============================================================
   百科知识大闯关 · 公共工具：进度存储 + 音效 + 通用函数
   ============================================================ */

// ---------- 进度存储（localStorage） ----------
var PROGRESS_KEY = "baike_quiz_progress_v1";

function loadProgress() {
  try {
    var raw = localStorage.getItem(PROGRESS_KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) { /* 忽略损坏数据 */ }
  return { currentLevel: 1, currentQuestion: 1, currentCorrect: 0, maxUnlocked: 1, doneLevels: [] };
}

function saveProgress(p) {
  try { localStorage.setItem(PROGRESS_KEY, JSON.stringify(p)); } catch (e) { /* 存储满则忽略 */ }
}

// ---------- 音效（Web Audio 合成，无外部文件） ----------
var Sound = (function () {
  var ctx = null;
  var enabled = true;
  try { enabled = localStorage.getItem("baike_quiz_sound") !== "off"; } catch (e) {}

  function ensure() {
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (AC) ctx = new AC();
    }
    return ctx;
  }

  function tone(freq, dur, type, gainVal, when) {
    if (!enabled) return;
    var c = ensure();
    if (!c) return;
    var t = c.currentTime + (when || 0);
    var osc = c.createOscillator();
    var g = c.createGain();
    osc.type = type || "sine";
    osc.frequency.setValueAtTime(freq, t);
    g.gain.setValueAtTime(gainVal || 0.15, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(g); g.connect(c.destination);
    osc.start(t); osc.stop(t + dur + 0.02);
  }

  return {
    correct: function () {
      tone(523, 0.12, "sine", 0.18);
      tone(659, 0.12, "sine", 0.18, 0.1);
      tone(784, 0.2, "sine", 0.18, 0.2);
    },
    wrong: function () {
      tone(220, 0.25, "sawtooth", 0.12);
      tone(174, 0.3, "sawtooth", 0.12, 0.12);
    },
    levelClear: function () {
      var notes = [523, 659, 784, 1047];
      notes.forEach(function (f, i) { tone(f, 0.16, "triangle", 0.2, i * 0.12); });
    },
    finish: function () {
      var notes = [523, 587, 659, 784, 880, 1047];
      notes.forEach(function (f, i) { tone(f, 0.2, "triangle", 0.2, i * 0.14); });
    },
    click: function () { tone(600, 0.05, "square", 0.06); },
    isEnabled: function () { return enabled; },
    toggle: function () {
      enabled = !enabled;
      try { localStorage.setItem("baike_quiz_sound", enabled ? "on" : "off"); } catch (e) {}
      return enabled;
    }
  };
})();

// ---------- Toast 提示 ----------
function showToast(msg) {
  var t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(function () { t.classList.remove("show"); }, 2000);
}
