/* ============================================================
   百科知识大闯关 · 闯关逻辑
   规则：每关 5 题，全部答对才算过关；答错本关重新开始（题目顺序打乱）
   ============================================================ */

(function () {
  var D = window.QUIZ_DATA;
  var perLevel = D.per_level;
  var totalLevels = D.total_levels;
  var ALL = D.questions;

  // 从 URL 读取关卡
  var qs = new URLSearchParams(location.search);
  var targetLevel = parseInt(qs.get("level"), 10);
  if (!targetLevel || targetLevel < 1 || targetLevel > totalLevels) targetLevel = 1;

  var prog = loadProgress();

  // 只允许挑战已解锁关卡
  if (targetLevel > prog.maxUnlocked) {
    targetLevel = Math.max(1, prog.maxUnlocked);
  }

  // ---------- 状态 ----------
  var state = {
    level: targetLevel,
    questions: [],   // 本关题目（乱序）
    qIndex: 0,       // 当前题下标
    correctCount: 0,
    answered: false,
    finished: false
  };

  // ---------- 初始化本关 ----------
  function buildLevel(level) {
    var pool = ALL.filter(function (q) { return q.level === level; });
    // Fisher-Yates 洗牌
    for (var i = pool.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = pool[i]; pool[i] = pool[j]; pool[j] = t;
    }
    state.questions = pool.slice(0, perLevel);
    state.qIndex = 0;
    state.correctCount = 0;
    state.answered = false;
    state.finished = false;
    renderHeader();
    renderQuestion();
  }

  function renderHeader() {
    document.getElementById("level-title").textContent = "第 " + state.level + " 关";
    document.getElementById("level-sub").textContent =
      "挑战 " + perLevel + " 题 · 全对过关" + (state.level > 1 ? " · 当前进度保存中" : "");
    document.getElementById("progress-fill").style.width =
      (state.correctCount / perLevel * 100) + "%";
  }

  function renderQuestion() {
    var q = state.questions[state.qIndex];
    state.answered = false;
    document.getElementById("q-index").textContent = "第 " + (state.qIndex + 1) + " / " + perLevel + " 题";
    document.getElementById("q-score").textContent = "连续答对 " + state.correctCount + " / " + perLevel;
    document.getElementById("q-text").textContent = q.text;
    document.getElementById("q-feedback").className = "feedback";
    document.getElementById("q-feedback").innerHTML = "";

    var optsBox = document.getElementById("q-options");
    optsBox.innerHTML = "";
    var letters = ["A", "B", "C", "D"];
    var items = [
      { key: "A", txt: q.option_a },
      { key: "B", txt: q.option_b },
      { key: "C", txt: q.option_c }
    ];
    if (q.option_d) items.push({ key: "D", txt: q.option_d });

    items.forEach(function (it) {
      if (!it.txt) return;
      var div = document.createElement("div");
      div.className = "option";
      div.innerHTML = '<span class="key">' + it.key + '</span><span>' + it.txt + '</span>';
      div.addEventListener("click", function () { choose(it.key, div); });
      optsBox.appendChild(div);
    });
  }

  function choose(key, el) {
    if (state.answered || state.finished) return;
    state.answered = true;
    var q = state.questions[state.qIndex];
    var opts = document.querySelectorAll(".option");
    opts.forEach(function (o) { o.classList.add("disabled"); });

    var fb = document.getElementById("q-feedback");
    if (key === q.answer) {
      // 答对
      el.classList.add("correct");
      state.correctCount++;
      Sound.correct();
      var expl = q.explanation ? '<div class="expl">💡 ' + q.explanation + '</div>' : "";
      fb.className = "feedback show ok";
      fb.innerHTML = "✅ 回答正确！" + expl;
      document.getElementById("progress-fill").style.width = (state.correctCount / perLevel * 100) + "%";

      if (state.correctCount >= perLevel) {
        // 本关全部答对 → 过关
        state.finished = true;
        setTimeout(onLevelClear, 900);
      } else {
        setTimeout(nextQuestion, 900);
      }
    } else {
      // 答错 → 标记正确答案 + 本关重来
      el.classList.add("wrong");
      opts.forEach(function (o) {
        var k = o.querySelector(".key").textContent;
        if (k === q.answer) o.classList.add("correct");
      });
      Sound.wrong();
      var expl = q.explanation ? '<div class="expl">💡 ' + q.explanation + '</div>' : "";
      fb.className = "feedback show bad";
      fb.innerHTML = "❌ 答错了，本关重新开始！" + expl;
      document.getElementById("progress-fill").style.width = "0%";
      setTimeout(function () { buildLevel(state.level); }, 1600);
    }
  }

  function nextQuestion() {
    state.qIndex++;
    state.answered = false;
    renderQuestion();
  }

  // ---------- 过关处理 ----------
  function onLevelClear() {
    Sound.levelClear();

    // 更新进度
    if (prog.doneLevels.indexOf(state.level) === -1) prog.doneLevels.push(state.level);
    prog.maxUnlocked = Math.max(prog.maxUnlocked, state.level + 1);
    if (state.level === totalLevels) {
      prog.maxUnlocked = totalLevels;
    }

    if (state.level < totalLevels) {
      prog.currentLevel = state.level + 1;
    }
    prog.currentQuestion = 1;
    prog.currentCorrect = 0;
    saveProgress(prog);

    // 结算弹层
    var isLast = state.level >= totalLevels;
    document.getElementById("result-emoji").textContent = isLast ? "🏆" : "🎉";
    document.getElementById("result-title").textContent = isLast ? "恭喜通关全部 40 关！" : "第 " + state.level + " 关 过关！";
    document.getElementById("result-desc").textContent = isLast
      ? "你已完成全部 " + totalLevels + " 关的挑战，知识达人就是你！"
      : "5 题全部答对，成功解锁第 " + (state.level + 1) + " 关！";
    var btnNext = document.getElementById("btn-next");
    if (isLast) {
      btnNext.textContent = "🏆 再来一遍";
      btnNext.onclick = function () {
        var fresh = { currentLevel: 1, currentQuestion: 1, currentCorrect: 0, maxUnlocked: 1, doneLevels: [] };
        saveProgress(fresh);
        location.href = "game.html?level=1";
      };
    } else {
      btnNext.textContent = "▶ 进入第 " + (state.level + 1) + " 关";
      btnNext.onclick = function () {
        location.href = "game.html?level=" + (state.level + 1);
      };
    }
    document.getElementById("overlay").classList.add("show");
  }

  // ---------- 音效开关 ----------
  var sToggle = document.getElementById("sound-toggle");
  function syncSoundIcon() { sToggle.textContent = Sound.isEnabled() ? "🔊" : "🔇"; }
  syncSoundIcon();
  sToggle.addEventListener("click", function () {
    Sound.toggle();
    syncSoundIcon();
    showToast(Sound.isEnabled() ? "🔊 音效已开启" : "🔇 音效已关闭");
  });

  // 首次进入：解锁检查提示
  if (targetLevel !== parseInt(qs.get("level"), 10)) {
    showToast("🔒 该关卡未解锁，已回到第 " + targetLevel + " 关");
  }

  // 启动
  buildLevel(targetLevel);
})();
