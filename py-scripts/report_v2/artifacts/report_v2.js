(function () {
  if (typeof window.echarts === "undefined") { return; }
  var PALETTE = __LF_PALETTE__;

  function initChart(el) {
    var dpr = Math.max(2, window.devicePixelRatio || 1);
    return window.echarts.init(el, null, { devicePixelRatio: dpr, renderer: window.__lfReportPdf ? "svg" : "canvas" });
  }

  function baseOption(yName, xName) {
    return {
      textStyle: { fontFamily: '"Segoe UI", Roboto, Arial, Helvetica, sans-serif' },
      color: PALETTE,
      tooltip: { trigger: "axis", axisPointer: { type: "cross" } },
      legend: { bottom: 0, textStyle: { color: "#5f6f82", fontSize: 12 }, itemWidth: 30, itemHeight: 14 },
      grid: { left: 76, right: 28, top: 48, bottom: 84, containLabel: true },
      xAxis: {
        type: "category", name: xName || "", nameLocation: "middle", nameGap: 34,
        nameTextStyle: { color: "#2c3e50", fontWeight: 600 },
        axisLine: { lineStyle: { color: "#c8d4e3" } },
        axisLabel: { color: "#2c3e50", fontWeight: 600 },
        splitLine: { show: true, lineStyle: { color: "#ecf1f6" } }
      },
      yAxis: {
        type: "value", name: yName || "", nameLocation: "middle", nameGap: 52, nameRotate: 90,
        nameTextStyle: { color: "#2c3e50", fontWeight: 600 },
        axisLine: { lineStyle: { color: "#c8d4e3" } },
        axisLabel: { color: "#5f6f82" },
        splitLine: { show: true, lineStyle: { color: "#ecf1f6" } }
      },
      dataZoom: [
        { type: "inside", xAxisIndex: 0 },
        { type: "slider", xAxisIndex: 0, bottom: 18, height: 18, brushSelect: false }
      ],
      series: []
    };
  }

  function renderFallback(id, message) {
    var el = document.getElementById(id);
    if (el) {
      el.innerHTML = '<div class="chart-fallback">' + (message || "Interactive chart unavailable.") + "</div>";
    }
  }

  window.__lfModernReport = window.__lfModernReport || {};

  var DATA_ZOOM_MIN_CATEGORIES = 10;

  function dropDataZoomIfFewCategories(option, categories) {
    if (!categories || categories.length < DATA_ZOOM_MIN_CATEGORIES) {
      option.dataZoom = [];
    }
  }

  function barMaxWidthFor(categories) {
    return (categories || []).length <= 6 ? 90 : 34;
  }

  window.__lfModernReport.renderLineChart = function (id, payload, yName, xName) {
    var el = document.getElementById(id);
    if (!el || !payload || !payload.series) { renderFallback(id); return; }
    var chart = initChart(el);
    var option = baseOption(yName, xName);
    if (payload.categories) { option.xAxis.data = payload.categories; option.xAxis.type = "category"; }
    if (payload.xAxisType === "value") { option.xAxis.type = "value"; }
    if (payload.clockOffsetSeconds !== undefined) {
      var clockLabel = function (value) {
        var seconds = ((Math.round(Number(value) + payload.clockOffsetSeconds) % 86400) + 86400) % 86400;
        return [Math.floor(seconds / 3600), Math.floor(seconds / 60) % 60, seconds % 60]
          .map(function (part) { return String(part).padStart(2, "0"); }).join(":");
      };
      option.xAxis.axisLabel.formatter = clockLabel;
      option.xAxis.axisLabel.rotate = 45;
      option.xAxis.nameGap = 60;
      option.grid.bottom = 110;
      option.xAxis.axisPointer = { label: { formatter: function (p) { return clockLabel(p.value); } } };
      option.tooltip.formatter = function (params) {
        return clockLabel(params[0].value[0]) + "<br/>" + params.map(function (p) {
          return p.marker + p.seriesName + ": " + p.value[1];
        }).join("<br/>");
      };
    }
    if (payload.inverseX) { option.xAxis.inverse = true; }
    if (payload.inverseY) { option.yAxis.inverse = true; }
    option.series = payload.series.map(function (s) {
      var c = s.color;
      return {
        name: s.name, type: "line", smooth: false, symbol: "none", connectNulls: false,
        data: s.data,
        lineStyle: { width: 2, color: c, type: s.dashed ? [6, 4] : "solid" },
        itemStyle: c ? { color: c } : undefined
      };
    });
    chart.setOption(option);
    window.addEventListener("resize", function () { chart.resize(); });
  };

  window.__lfModernReport.renderBarChart = function (id, payload, yName, xName) {
    var el = document.getElementById(id);
    if (!el || !payload || !payload.series) { renderFallback(id); return; }
    var chart = initChart(el);
    var option = baseOption(yName, xName);
    option.tooltip.axisPointer = { type: "shadow" };
    option.xAxis.data = payload.categories || [];
    dropDataZoomIfFewCategories(option, payload.categories);
    var barMaxWidth = barMaxWidthFor(payload.categories);
    var perCategoryColor = payload.categories && payload.series.length === 1 &&
      payload.series[0].data.every(function (d) { return d && typeof d === "object" && d.itemStyle && d.itemStyle.color; });
    if (perCategoryColor) {
      option.legend.data = payload.categories;
      option.series = payload.categories.map(function (cat, i) {
        var point = payload.series[0].data[i];
        var row = payload.categories.map(function () { return null; });
        row[i] = point.value;
        return {
          name: cat, type: "bar", data: row, barMaxWidth: barMaxWidth,
          barGap: "-100%", barCategoryGap: "20%",
          itemStyle: { color: point.itemStyle.color }
        };
      });
    } else {
      option.series = payload.series.map(function (s) {
        var c = s.color;
        return {
          name: s.name, type: "bar", data: s.data, barMaxWidth: barMaxWidth,
          stack: payload.stacked ? "total" : undefined,
          itemStyle: c ? { color: c } : undefined
        };
      });
    }
    if (payload.itemDetails) {
      option.tooltip.trigger = "item";
      option.tooltip.formatter = function (p) {
        var details = (payload.itemDetails[p.name] || {})[p.seriesName] || [];
        var body = details.length
          ? details.map(function (t) { return "&nbsp;&nbsp;" + t; }).join("<br/>")
          : "&nbsp;&nbsp;<i>none</i>";
        return "<b>" + p.name + "</b> &mdash; " + p.marker + " <b>" + p.seriesName + "</b><br/>" + body;
      };
    }
    chart.setOption(option);
    window.addEventListener("resize", function () { chart.resize(); });
  };

  window.__lfModernReport.renderHorizontalBarChart = function (id, payload, xName, yName) {
    var el = document.getElementById(id);
    if (!el || !payload || !payload.series) { renderFallback(id); return; }
    el.style.height = Math.max(300, (payload.categories || []).length * 52 + 120) + "px";
    var chart = initChart(el);
    var option = baseOption(yName, xName);
    option.grid = { left: 70, right: 28, top: 48, bottom: 84, containLabel: true };
    option.xAxis = {
      type: "value", name: xName || "", min: 0,
      nameLocation: "middle", nameGap: 30,
      nameTextStyle: { color: "#2c3e50", fontWeight: 600, fontSize: 13 },
      axisLabel: { color: "#5f6f82" }
    };
    option.yAxis = {
      type: "category", data: payload.categories || [],
      name: payload.yAxisName || yName || "", nameLocation: "middle", nameGap: 115, nameRotate: 90,
      nameTextStyle: { color: "#2c3e50", fontWeight: 600, fontSize: 13 },
      axisLabel: {
        color: "#2c3e50", fontWeight: 600,
        formatter: function (value) { return value.length > 9 ? value.slice(0, 9) + "…" : value; }
      }
    };
    option.series = payload.series.map(function (s) {
      var c = s.color;
      return {
        name: s.name, type: "bar", data: s.data,
        stack: payload.stacked ? "total" : undefined,
        itemStyle: c ? { color: c } : undefined,
        label: { show: true, color: payload.stacked ? "#ffffff" : "#2c3e50", position: payload.stacked ? "inside" : "right" }
      };
    });
    chart.setOption(option);
    window.addEventListener("resize", function () { chart.resize(); });
  };

  window.__lfModernReport.renderConnectivityTimeline = function (id, payload) {
    var el = document.getElementById(id);
    var clients = (payload && payload.clients) || [];
    var stations = (payload && payload.stations) || [];
    var segments = (payload && payload.segments) || [];
    if (!el || !clients.length || !segments.length) {
      renderFallback(id, payload && payload.emptyMessage);
      return;
    }

    el.style.height = Math.max(320, clients.length * 38 + 150) + "px";
    var chart = initChart(el);

    function renderSegment(params, api) {
      var category = api.value(0);
      var start = api.coord([api.value(1), category]);
      var end = api.coord([api.value(2), category]);
      var height = api.size([0, 1])[1] * 0.56;
      var shape = echarts.graphic.clipRectByRect({
        x: start[0],
        y: start[1] - height / 2,
        width: Math.max(end[0] - start[0], 1),
        height: height
      }, {
        x: params.coordSys.x,
        y: params.coordSys.y,
        width: params.coordSys.width,
        height: params.coordSys.height
      });
      return shape && { type: "rect", shape: shape, style: api.style() };
    }

    function seriesFor(status, label, color) {
      return {
        name: label,
        type: "custom",
        renderItem: renderSegment,
        itemStyle: { color: color },
        encode: { x: [1, 2], y: 0 },
        data: segments.filter(function (s) { return s.status === status; })
          .map(function (s) { return [s.clientIndex, s.start, s.end]; })
      };
    }

    chart.setOption({
      tooltip: {
        trigger: "item",
        formatter: function (p) {
          var values = p.value || [];
          var station = stations[values[0]];
          var stationLine = station ? " (" + station + ")" : "";
          return p.marker + " <b>" + clients[values[0]] + "</b>" + stationLine + "<br/>" +
            p.seriesName + ": " + Number(values[1]).toFixed(1) + "–" +
            Number(values[2]).toFixed(1) + " s";
        }
      },
      legend: { bottom: 0, data: [payload.connectedLabel || "Up", "Drop"], textStyle: { color: "#5f6f82" } },
      grid: { left: 165, right: 30, top: 25, bottom: 72, containLabel: false },
      xAxis: {
        type: "value",
        min: 0,
        max: payload.duration,
        name: payload.xAxisName || "Time (seconds)",
        nameLocation: "middle",
        nameGap: 36,
        axisLabel: { color: "#5f6f82" },
        splitLine: { lineStyle: { color: "#ecf1f6" } }
      },
      yAxis: {
        type: "category",
        inverse: true,
        data: clients,
        name: payload.yAxisName || "", nameLocation: "middle", nameGap: 150,
        axisLabel: { color: "#2c3e50", fontWeight: 600, width: 145, overflow: "truncate" },
        axisTick: { show: false },
        axisLine: { show: false }
      },
      series: [
        seriesFor("up", payload.connectedLabel || "Up", "#2e8b57"),
        seriesFor("drop", "Drop", "#eb5757")
      ]
    });
    window.addEventListener("resize", function () { chart.resize(); });
  };

  window.__lfModernReport.renderPieChart = function (id, payload) {
    var el = document.getElementById(id);
    if (!el || !payload || !payload.slices || !payload.slices.length) {
      renderFallback(id, payload && payload.emptyMessage);
      return;
    }
    var chart = initChart(el);
    var showPct = !!payload.showPercentage;
    var labelFmt = payload.labelFormatter || (showPct ? "{b}\n{d}%" : "{b}\n{c}");
    var tooltipFmt = payload.tooltipFormatter || "{b}: {c} ({d}%)";
    function formatPieLabel(p) {
      if (!(Number(p.value) > 0)) { return ""; }
      return String(labelFmt)
        .replace(/\{b\}/g, p.name)
        .replace(/\{c\}/g, p.value)
        .replace(/\{d\}/g, p.percent);
    }
    var option = {
      color: payload.colors || PALETTE,
      tooltip: { trigger: "item", formatter: tooltipFmt },
      legend: (payload.legend === false) ? { show: false } : { bottom: 0, textStyle: { color: "#5f6f82", fontSize: 12 } },
      series: [{
        type: "pie",
        radius: payload.radius || ["38%", "68%"],
        center: payload.center || ["50%", "44%"],
        stillShowZeroSum: false,
        label: (payload.showLabels === false) ? { show: false } : { formatter: formatPieLabel },
        labelLine: { show: payload.showLabels !== false },
        itemStyle: { borderWidth: 0 },
        data: payload.slices
      }]
    };
    if (payload.itemDetails) {
      option.tooltip.formatter = function (p) {
        var items = payload.itemDetails[p.name] || [];
        var body = items.length
          ? items.map(function (t) { return "&nbsp;&nbsp;" + t; }).join("<br/>")
          : "&nbsp;&nbsp;<i>none</i>";
        return p.marker + " <b>" + p.name + "</b>: " + p.value + " (" + p.percent + "%)<br/>" + body;
      };
    }
    if (payload.centerLabel) {
      var main = (typeof payload.centerLabel === "object") ? (payload.centerLabel.main || "") : String(payload.centerLabel);
      var sub = (typeof payload.centerLabel === "object") ? (payload.centerLabel.sub || "") : "";
      option.graphic = [{
        type: "text",
        left: "center",
        top: (payload.center && payload.center[1]) || "44%",
        style: {
          text: sub ? (main + "\n" + sub) : main,
          textAlign: "center",
          fill: "#2c3e50",
          fontSize: 20,
          fontWeight: 700,
          lineHeight: 24
        }
      }];
    }
    chart.setOption(option);
    window.addEventListener("resize", function () { chart.resize(); });
  };
})();

(function () {
  window.__lfModernReport = window.__lfModernReport || {};

  // rows: [{cellsHtml: "<td>...</td><td>...</td>"}]
  window.__lfModernReport.initSearchTable = function (rootId, rows, pageSize) {
    var root = document.getElementById(rootId);
    if (!root) { return; }
    var tbody = root.querySelector(".device-table tbody");
    var pageSizeSelect = root.querySelector(".rows-per-page select");
    var paginationEl = root.querySelector(".pagination");
    var countEl = root.querySelector(".device-count-label");
    var viewAllBtn = root.querySelector(".view-all-btn");
    if (!tbody) { return; }

    var state = { filtered: rows, page: 1, pageSize: pageSize || rows.length || 10 };

    function renderRows() {
      var total = state.filtered.length;
      var pages = Math.max(1, Math.ceil(total / state.pageSize));
      if (state.page > pages) { state.page = pages; }
      var start = (state.page - 1) * state.pageSize;
      var pageRows = state.filtered.slice(start, start + state.pageSize);
      tbody.innerHTML = pageRows.map(function (r, i) {
        return "<tr><td>" + (start + i + 1) + "</td>" + r.cellsHtml + "</tr>";
      }).join("") || "<tr><td colspan='99' style='text-align:center;color:var(--muted);'>No matching rows</td></tr>";
      renderPagination(pages);
    }

    function renderPagination(pages) {
      if (!paginationEl) { return; }
      var parts = [];
      parts.push('<button data-page="' + (state.page - 1) + '"' + (state.page === 1 ? " disabled" : "") + ">&lsaquo;</button>");
      var shown = [];
      for (var p = 1; p <= pages; p++) {
        if (p === 1 || p === pages || Math.abs(p - state.page) <= 1) { shown.push(p); }
        else if (shown[shown.length - 1] !== "...") { shown.push("..."); }
      }
      shown.forEach(function (p) {
        if (p === "...") { parts.push('<span class="pagination-ellipsis">&hellip;</span>'); }
        else { parts.push('<button data-page="' + p + '" class="' + (p === state.page ? "active" : "") + '">' + p + "</button>"); }
      });
      parts.push('<button data-page="' + (state.page + 1) + '"' + (state.page === pages ? " disabled" : "") + ">&rsaquo;</button>");
      paginationEl.innerHTML = parts.join("");
      Array.prototype.forEach.call(paginationEl.querySelectorAll("button[data-page]"), function (btn) {
        btn.addEventListener("click", function () {
          state.page = parseInt(btn.getAttribute("data-page"), 10);
          renderRows();
        });
      });
    }

    if (pageSizeSelect) {
      pageSizeSelect.addEventListener("change", function () {
        state.pageSize = pageSizeSelect.value === "all" ? rows.length : parseInt(pageSizeSelect.value, 10);
        state.page = 1;
        renderRows();
      });
    }
    if (viewAllBtn) {
      viewAllBtn.addEventListener("click", function () {
        state.pageSize = rows.length || 1;
        state.page = 1;
        if (pageSizeSelect) { pageSizeSelect.value = "all"; }
        renderRows();
      });
    }
    renderRows();
  };
})();

document.addEventListener("DOMContentLoaded", function () {
  (function () {
    function cellSortValue(cell) {
      var text = cell.textContent.trim();
      var numeric = parseFloat(text.replace(/,/g, ""));
      if (!isNaN(numeric) && /^-?[\d.,]+/.test(text)) { return numeric; }
      return text.toLowerCase();
    }

    function sortTable(table, columnIndex, ascending) {
      var tbody = table.tBodies[0];
      if (!tbody) { return; }
      var rows = Array.prototype.slice.call(tbody.rows);
      rows.sort(function (rowA, rowB) {
        var a = cellSortValue(rowA.cells[columnIndex]);
        var b = cellSortValue(rowB.cells[columnIndex]);
        if (a < b) { return ascending ? -1 : 1; }
        if (a > b) { return ascending ? 1 : -1; }
        return 0;
      });
      rows.forEach(function (row) { tbody.appendChild(row); });
    }

    Array.prototype.forEach.call(document.querySelectorAll("table.data-table"), function (table) {
      var headerRow = table.tHead && table.tHead.rows[0];
      if (!headerRow || !table.tBodies.length) { return; }
      Array.prototype.forEach.call(headerRow.cells, function (th, columnIndex) {
        th.classList.add("sortable");
        th.addEventListener("click", function () {
          var ascending = !th.classList.contains("sort-asc");
          Array.prototype.forEach.call(headerRow.cells, function (cell) {
            cell.classList.remove("sort-asc", "sort-desc");
          });
          th.classList.add(ascending ? "sort-asc" : "sort-desc");
          sortTable(table, columnIndex, ascending);
        });
      });
    });
  })();

  (function () {
    var tables = Array.prototype.slice.call(document.querySelectorAll("table.data-table"))
      .filter(function (table) { return table.tBodies.length > 0; });
    if (!tables.length) { return; }

    var searchBar = document.createElement("div");
    searchBar.className = "table-search-bar";
    var input = document.createElement("input");
    input.type = "text";
    input.className = "table-search-input";
    input.placeholder = "Search for a device, value, or anything else across every table below\u2026";
    var count = document.createElement("span");
    count.className = "table-search-count";
    searchBar.appendChild(input);
    searchBar.appendChild(count);

    var anchorCard = null;
    Array.prototype.forEach.call(document.querySelectorAll(".info-card"), function (card) {
      var header = card.querySelector(".info-card-header");
      var text = header && header.textContent.trim();
      if (text === "Key Findings") { anchorCard = card; }
      else if (text === "Overall Test Verdict" && !anchorCard) { anchorCard = card; }
    });
    if (anchorCard) {
      anchorCard.parentNode.insertBefore(searchBar, anchorCard.nextSibling);
    } else {
      var firstWrap = tables[0].closest(".table-wrap") || tables[0].parentNode;
      firstWrap.parentNode.insertBefore(searchBar, firstWrap);
    }

    function applyFilter() {
      var query = input.value.trim().toLowerCase();
      var shown = 0, total = 0;
      tables.forEach(function (table) {
        Array.prototype.forEach.call(table.tBodies[0].rows, function (row) {
          total++;
          var match = !query || row.textContent.toLowerCase().indexOf(query) !== -1;
          row.style.display = match ? "" : "none";
          if (match) { shown++; }
        });
      });
      count.textContent = query ? (shown + " / " + total + " rows across " + tables.length + " tables") : "";
    }
    input.addEventListener("input", applyFilter);
  })();
});
