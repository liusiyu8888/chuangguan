/* ============================================================
   百科知识大闯关 · 学习模式：浏览全部题目，可搜索 / 按关卡筛选
   ============================================================ */

(function () {
  var D = window.QUIZ_DATA;
  var ALL = D.questions;
  var totalLevels = D.total_levels;
  var showAllAnswers = false;

  document.getElementById("study-total").textContent = ALL.length;

  // 填充关卡筛选下拉
  var sel = document.getElementById("level-filter");
  for (var i = 1; i <= totalLevels; i++) {
    var opt = document.createElement("option");
    opt.value = String(i);
    opt.textContent = "第 " + i + " 关";
    sel.appendChild(opt);
  }

  var listBox = document.getElementById("q-list");
  var emptyBox = document.getElementById("q-empty");

  function letters() { return ["A", "B", "C", "D"]; }

  function render() {
    var kw = document.getElementById("search-box").value.trim().toLowerCase();
    var lv = parseInt(document.getElementById("level-filter").value, 10);

    var items = ALL.filter(function (q) {
      if (lv > 0 && q.level !== lv) return false;
      if (kw) {
        var hay = (q.text + q.option_a + q.option_b + q.option_c + (q.option_d || "")).toLowerCase();
        if (hay.indexOf(kw) === -1) return false;
      }
      return true;
    });

    listBox.innerHTML = "";
    if (items.length === 0) {
      emptyBox.style.display = "block";
      return;
    }
    emptyBox.style.display = "none";

    var letters = ["A", "B", "C", "D"];
    items.forEach(function (q) {
      var item = document.createElement("div");
      item.className = "panel q-item";

      var optsHtml = "";
      var optData = [
        { k: "A", v: q.option_a },
        { k: "B", v: q.option_b },
        { k: "C", v: q.option_c }
      ];
      if (q.option_d) optData.push({ k: "D", v: q.option_d });
      optData.forEach(function (o) {
        if (!o.v) return;
        var cls = (showAllAnswers && o.k === q.answer) ? "opt-line correct-ans" : "opt-line";
        optsHtml += '<div class="' + cls + '"><span>' + o.k + '.</span><span>' + o.v + '</span></div>';
      });

      var ansHtml = showAllAnswers
        ? '<div class="ans">✅ 正确答案：' + q.answer + '</div>'
        : '<div class="ans" style="color:var(--dim);">答案已隐藏 · <a href="javascript:void(0)" data-show="' + q.id + '" style="color:var(--cyan);">显示答案</a></div>';

      var explHtml = (showAllAnswers && q.explanation)
        ? '<div class="expl">💡 ' + q.explanation + '</div>'
        : "";

      item.innerHTML =
        '<div class="idx">第 ' + q.level + ' 关 · 第 ' + q.id + ' 题</div>' +
        '<div class="txt">' + q.text + '</div>' +
        '<div class="opts">' + optsHtml + '</div>' +
        ansHtml + explHtml;

      // 单个显示答案
      var link = item.querySelector('a[data-show]');
      if (link) {
        link.addEventListener("click", function () {
          var qid = parseInt(this.getAttribute("data-show"), 10);
          var qq = ALL.filter(function (x) { return x.id === qid; })[0];
          if (!qq) return;
          showAllAnswers = true;
          // 全局显示
          render();
          showToast("✅ 已显示答案（共 " + qq.answer + "）");
        });
      }

      listBox.appendChild(item);
    });
  }

  // 事件绑定
  document.getElementById("search-box").addEventListener("input", render);
  document.getElementById("level-filter").addEventListener("change", render);
  document.getElementById("btn-toggle-answers").addEventListener("click", function () {
    showAllAnswers = !showAllAnswers;
    this.textContent = showAllAnswers ? "🙈 隐藏全部答案" : "👀 显示全部答案";
    render();
    showToast(showAllAnswers ? "👀 已显示全部答案" : "🙈 已隐藏全部答案");
  });

  render();
})();
