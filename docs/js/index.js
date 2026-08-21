/* ============================================================
   百科知识大闯关 · 首页逻辑：关卡地图 + 进度统计 + 重置
   ============================================================ */

(function () {
  var D = window.QUIZ_DATA;
  var perLevel = D.per_level;
  var totalLevels = D.total_levels;
  var prog = loadProgress();

  // 统计
  document.getElementById("stat-questions").textContent = D.questions.length;
  document.getElementById("stat-levels").textContent = totalLevels;
  document.getElementById("stat-unlocked").textContent = prog.maxUnlocked;
  document.getElementById("stat-current").textContent = prog.currentLevel;

  // 渲染关卡地图
  var grid = document.getElementById("level-grid");
  grid.innerHTML = "";
  for (var i = 1; i <= totalLevels; i++) {
    var card = document.createElement("a");
    card.className = "level-card";
    var isDone = prog.doneLevels.indexOf(i) !== -1;
    var isCurrent = i === prog.currentLevel;
    var isLocked = i > prog.maxUnlocked;

    if (isLocked) {
      card.classList.add("locked");
      card.href = "javascript:void(0)";
    } else {
      card.href = "game.html?level=" + i;
    }
    if (isDone) card.classList.add("done");
    if (isCurrent) card.classList.add("current");

    var st = isLocked ? "🔒 未解锁" : (isDone ? "✅ 已通关" : (isCurrent ? "🔥 进行中" : "可挑战"));
    card.innerHTML =
      '<div class="lv">第 ' + i + ' 关</div>' +
      '<div class="st">' + st + '</div>' +
      (isDone ? '<span class="badge">通关</span>' : "");
    card.addEventListener("click", function (e) {
      if (this.classList.contains("locked")) {
        e.preventDefault();
        showToast("🔒 先通关前面的关卡才能挑战");
        Sound.click();
      } else {
        Sound.click();
      }
    });
    grid.appendChild(card);
  }

  // 重置进度
  document.getElementById("btn-reset").addEventListener("click", function () {
    if (confirm("确定要重置全部闯关进度吗？")) {
      var fresh = { currentLevel: 1, currentQuestion: 1, currentCorrect: 0, maxUnlocked: 1, doneLevels: [] };
      saveProgress(fresh);
      showToast("✅ 进度已重置");
      setTimeout(function () { location.reload(); }, 600);
    }
  });
})();
