#!/usr/bin/env python3
"""
NAME: lf_graph_v2.py

PURPOSE:

- A newer version of lf_graph.py, used with lf_report_v2.py.
- The chart classes take the same arguments as in lf_graph.py, so existing
  scripts only need to change the import.
- Charts are interactive (ECharts) instead of matplotlib PNG images.
  Pass the result of build_*_graph() to report.set_graph_image().

EXAMPLE:
    from report_v2.lf_graph_v2 import lf_pie_graph

    pie = lf_pie_graph(_data_set=[70, 30], _label=["Online", "Offline"], _graph_title="Status")
    report.set_graph_image(pie.build_pie_graph())
    report.build_graph()

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright (C) 2020-2026 Candela Technologies Inc

INCLUDE_IN_README
"""
import importlib
import json
import logging
import sys
from pathlib import Path

_py_scripts_dir = Path(__file__).resolve().parent.parent
_repo_root = _py_scripts_dir.parent
for _import_root in (_py_scripts_dir, _repo_root):
    if str(_import_root) not in sys.path:
        sys.path.append(str(_import_root))

logger = logging.getLogger(__name__)
lf_csv = importlib.import_module("py-scripts.lf_csv").lf_csv

# Chart colors (same palette as lf_report_v2.py).
_ECHARTS_PALETTE = ["#2a78d6", "#d0662a", "#1a9fb4", "#7650c8", "#b03a7d", "#5a6fd1"]

# Converts matplotlib color letters like 'r', 'g', 'b' to CSS colors.
_MPL_SHORTHAND_COLORS = {
    'r': 'red', 'g': 'green', 'b': 'blue', 'c': 'cyan',
    'm': 'magenta', 'y': '#bfbf00', 'k': 'black', 'w': 'white',
}


def _css_color(c):
    """Turns matplotlib short color codes (like 'r' or 'g') into CSS color names.

    Args:
        c: a color, e.g. 'r' or '#1f6f58'.

    Returns:
        the matching CSS color name, or c unchanged if it wasn't a short code.

    Example:
        css_color = _css_color('r')
    """
    return _MPL_SHORTHAND_COLORS.get(c, c) if isinstance(c, str) else c


class lf_bar_graph:
    """Interactive grouped/stacked vertical bar chart for use with
    lf_report.set_graph_image()/build_graph().

    Example:
        bar = lf_bar_graph(_data_set=[[10, 20, 30]], _xaxis_categories=["A", "B", "C"])
        report.set_graph_image(bar.build_bar_graph())
        report.build_graph()
    """

    def __init__(self, _data_set=None,
                 _xaxis_name="x-axis",
                 _yaxis_name="y-axis",
                 _xaxis_categories=None,
                 _xaxis_label=None,
                 _graph_title="",
                 _title_size=16,
                 _graph_image_name="image_name",
                 _label=None,
                 _color=None,
                 _bar_width=0.25,
                 _color_edge='grey',
                 _font_weight='bold',
                 _color_name=None,
                 _figsize=(10, 5),
                 _show_bar_value=False,
                 _xaxis_step=1,
                 _xticks_font=None,
                 _xaxis_value_location=0,
                 _xticks_rotation=None,
                 _text_font=None,
                 _text_rotation=None,
                 _grp_title="",
                 _legend_handles=None,
                 _legend_loc="best",
                 _legend_box=None,
                 _legend_ncol=1,
                 _legend_fontsize=None,
                 _dpi=96,
                 _enable_csv=False,
                 _remove_border=None,
                 _alignment=None,
                 _stacked=False,
                 _extra_payload=None,
                 _description=""
                 ):
        """Stores the bar chart data and options.

        Args:
            _data_set (list): one list of values per series/bar group.
            _xaxis_name (str): x-axis label.
            _yaxis_name (str): y-axis label.
            _xaxis_categories (list): tick values shown on the x-axis.
            _xaxis_label (list): tick text shown on the x-axis instead of _xaxis_categories,
                if it's the same length as the data.
            _graph_title (str): chart title.
            _graph_image_name (str): chart id, and the CSV file name when _enable_csv is True.
            _label (list): one name per series, used in the legend.
            _color (list): one color per series/bar; falls back to _color_name.
            _color_name (list): palette to use when _color isn't given.
            _enable_csv (bool): also save the data as a CSV file.
            _stacked (bool): stack the bars instead of placing them side by side.
            _extra_payload (dict): extra chart options merged into the chart payload.
            _description (str): text shown under the chart title.

            Most other options (_bar_width, _color_edge, _font_weight, _figsize,
            _show_bar_value, _xaxis_step, _xticks_font, _xaxis_value_location,
            _xticks_rotation, _text_font, _text_rotation, _grp_title, _legend_*, _dpi,
            _remove_border, _alignment, _title_size) are matplotlib-only: they're accepted so
            old callers keep working, but this interactive version doesn't use them.
        """
        if _data_set is None:
            _data_set = [[30.4, 55.3, 69.2, 37.1], [45.1, 67.2, 34.3, 22.4], [22.5, 45.6, 12.7, 34.8]]
        if _xaxis_categories is None:
            _xaxis_categories = [1, 2, 3, 4]
        # No default for _xaxis_label: it would replace the real x-axis categories.
        if _label is None:
            _label = ["bi-downlink", "bi-uplink", 'uplink']
        if _color_name is None:
            # Use the brand palette by default.
            _color_name = list(_ECHARTS_PALETTE)
        self.data_set = _data_set
        self.xaxis_name = _xaxis_name
        self.yaxis_name = _yaxis_name
        self.xaxis_categories = _xaxis_categories
        self.xaxis_label = _xaxis_label
        self.title = _graph_title
        self.title_size = _title_size
        self.graph_image_name = _graph_image_name
        self.label = _label
        self.color = _color
        self.bar_width = _bar_width
        self.color_edge = _color_edge
        self.font_weight = _font_weight
        self.color_name = _color_name
        self.figsize = _figsize
        self.show_bar_value = _show_bar_value
        self.xaxis_step = _xaxis_step
        self.xticks_font = _xticks_font
        self._xaxis_value_location = _xaxis_value_location
        self.text_font = _text_font
        self.text_rotation = _text_rotation
        self.grp_title = _grp_title
        self.enable_csv = _enable_csv
        self.legend_handles = _legend_handles
        self.legend_loc = _legend_loc
        self.legend_box = _legend_box
        self.legend_ncol = _legend_ncol
        self.legend_fontsize = _legend_fontsize
        self.remove_border = _remove_border
        self.alignment = _alignment
        self.xticks_rotation = _xticks_rotation
        self.stacked = _stacked
        self.extra_payload = _extra_payload
        self.description = _description

    def build_bar_graph(self):
        """Returns the interactive bar chart as HTML for set_graph_image().
        Also saves <graph_image_name>.csv when _enable_csv is True.

        Returns:
            str: chart-card HTML markup.

        Example:
            html = bar.build_bar_graph()
        """
        colors = self.color if self.color is not None else self.color_name
        # One series: each bar gets its own color. Several series: one color per series.
        if len(self.data_set) == 1:
            series = [{
                "name": self.label[0] if self.label else "series-0",
                "data": [
                    {"value": v, "itemStyle": {"color": _css_color(colors[i % len(colors)])}}
                    for i, v in enumerate(self.data_set[0])
                ],
            }]
        else:
            series = [
                {
                    "name": self.label[i] if i < len(self.label) else "series-{}".format(i),
                    "data": self.data_set[i],
                    "color": _css_color(colors[i % len(colors)]),
                }
                for i in range(len(self.data_set))
            ]

        if self.xaxis_label and len(self.xaxis_label) == len(self.data_set[0]):
            categories = [str(c) for c in self.xaxis_label]
        else:
            categories = [str(c) for c in self.xaxis_categories]

        payload = {"categories": categories, "series": series}
        if self.stacked:
            payload["stacked"] = True
        if self.extra_payload:
            payload.update(self.extra_payload)

        extra_args = ", {y}, {x}".format(y=json.dumps(self.yaxis_name), x=json.dumps(self.xaxis_name))
        markup = """
                <div class='chart-card'>
                  {title_html}
                  {description_html}
                  <div id='{chart_id}' class='chart'></div>
                  <script>
                    window.__lfModernReport.renderBarChart({chart_id_json}, {payload}{extra_args});
                  </script>
                </div>
                """.format(
            title_html=("<h3>{}</h3>".format(self.title) if self.title else ""),
            description_html=("<p align='left'>{}</p>".format(self.description) if self.description else ""),
            chart_id=self.graph_image_name,
            chart_id_json=json.dumps(self.graph_image_name),
            payload=json.dumps(payload),
            extra_args=extra_args,
        )

        if self.enable_csv:
            if self.xaxis_categories is not None and len(self.xaxis_categories) == len(self.data_set[0]):
                lf_csv_obj = lf_csv()
                lf_csv_obj.columns = [self.xaxis_name] + list(self.label)
                lf_csv_obj.rows = [self.xaxis_categories] + list(self.data_set)
                lf_csv_obj.filename = "{}.csv".format(self.graph_image_name)
                lf_csv_obj.generate_csv()
            else:
                raise ValueError("Length and x-axis values and y-axis values should be same.")

        return markup


class lf_bar_graph_horizontal:
    """Interactive grouped/stacked horizontal bar chart for use with
    lf_report.set_graph_image()/build_graph().

    Example:
        bar = lf_bar_graph_horizontal(_data_set=[[10, 20, 30]], _yaxis_categories=["A", "B", "C"])
        report.set_graph_image(bar.build_bar_graph_horizontal())
        report.build_graph()
    """

    def __init__(self, _data_set=None,
                 _xaxis_name="x-axis",
                 _yaxis_name="y-axis",
                 _yaxis_categories=None,
                 _yaxis_label=None,
                 _graph_title="",
                 _title_size=16,
                 _graph_image_name="image_name",
                 _label=None,
                 _color=None,
                 _bar_height=0.25,
                 _color_edge='grey',
                 _font_weight='bold',
                 _color_name=None,
                 _figsize=(10, 5),
                 _show_bar_value=False,
                 _yaxis_step=1,
                 _yticks_font=None,
                 _yaxis_value_location=0,
                 _yticks_rotation=None,
                 _text_font=None,
                 _text_rotation=None,
                 _grp_title="",
                 _legend_handles=None,
                 _legend_loc="best",
                 _legend_box=None,
                 _legend_ncol=1,
                 _legend_fontsize=None,
                 _dpi=96,
                 _enable_csv=False,
                 _remove_border=None,
                 _alignment=None,
                 _stacked=False,
                 _description=""
                 ):
        """Stores the horizontal bar chart data and options.

        Args:
            _data_set (list): one list of values per series/bar group.
            _xaxis_name (str): x-axis label.
            _yaxis_name (str): y-axis label.
            _yaxis_categories (list): tick values shown on the y-axis.
            _yaxis_label (list): tick text shown on the y-axis instead of _yaxis_categories,
                if it's the same length as the data.
            _graph_title (str): chart title.
            _graph_image_name (str): chart id, and the CSV file name when _enable_csv is True.
            _label (list): one name per series, used in the legend.
            _color (list): one color per series/bar; falls back to _color_name.
            _color_name (list): palette to use when _color isn't given.
            _enable_csv (bool): also save the data as a CSV file.
            _stacked (bool): stack the bars instead of placing them side by side.
            _description (str): text shown under the chart title.

            Most other options (_bar_height, _color_edge, _font_weight, _figsize,
            _show_bar_value, _yaxis_step, _yticks_font, _yaxis_value_location,
            _yticks_rotation, _text_font, _text_rotation, _grp_title, _legend_*, _dpi,
            _remove_border, _alignment, _title_size) are matplotlib-only: they're accepted so
            old callers keep working, but this interactive version doesn't use them.
        """
        if _data_set is None:
            _data_set = [[30.4, 55.3, 69.2, 37.1], [45.1, 67.2, 34.3, 22.4], [22.5, 45.6, 12.7, 34.8]]
        if _yaxis_categories is None:
            _yaxis_categories = [1, 2, 3, 4]
        # No default for _yaxis_label: it would replace the real y-axis categories.
        if _label is None:
            _label = ["bi-downlink", "bi-uplink", 'uplink']
        if _color_name is None:
            # Use the brand palette by default.
            _color_name = list(_ECHARTS_PALETTE)
        self.data_set = _data_set
        self.xaxis_name = _xaxis_name
        self.yaxis_name = _yaxis_name
        self.yaxis_categories = _yaxis_categories
        self.yaxis_label = _yaxis_label
        self.title = _graph_title
        self.title_size = _title_size
        self.graph_image_name = _graph_image_name
        self.label = _label
        self.color = _color
        self.bar_height = _bar_height
        self.color_edge = _color_edge
        self.font_weight = _font_weight
        self.color_name = _color_name
        self.figsize = _figsize
        self.show_bar_value = _show_bar_value
        self.yaxis_step = _yaxis_step
        self.yticks_font = _yticks_font
        self._yaxis_value_location = _yaxis_value_location
        self.text_font = _text_font
        self.text_rotation = _text_rotation
        self.grp_title = _grp_title
        self.enable_csv = _enable_csv
        self.legend_handles = _legend_handles
        self.legend_loc = _legend_loc
        self.legend_box = _legend_box
        self.legend_ncol = _legend_ncol
        self.legend_fontsize = _legend_fontsize
        self.remove_border = _remove_border
        self.alignment = _alignment
        self.yticks_rotation = _yticks_rotation
        self.stacked = _stacked
        self.description = _description

    def build_bar_graph_horizontal(self):
        """Returns the interactive horizontal bar chart as HTML for set_graph_image().
        Also saves <graph_image_name>.csv when _enable_csv is True.

        Returns:
            str: chart-card HTML markup.

        Example:
            html = bar.build_bar_graph_horizontal()
        """
        colors = self.color if self.color is not None else self.color_name
        series = [
            {
                "name": self.label[i] if i < len(self.label) else "series-{}".format(i),
                "data": self.data_set[i],
                "color": _css_color(colors[i % len(colors)]),
            }
            for i in range(len(self.data_set))
        ]

        if self.yaxis_label and len(self.yaxis_label) == len(self.data_set[0]):
            categories = [str(c) for c in self.yaxis_label]
        else:
            categories = [str(c) for c in self.yaxis_categories]

        payload = {"categories": categories, "series": series}
        if self.stacked:
            payload["stacked"] = True

        extra_args = ", {x}, {y}".format(x=json.dumps(self.xaxis_name), y=json.dumps(self.yaxis_name))
        markup = """
                <div class='chart-card'>
                  {title_html}
                  {description_html}
                  <div id='{chart_id}' class='chart'></div>
                  <script>
                    window.__lfModernReport.renderHorizontalBarChart({chart_id_json}, {payload}{extra_args});
                  </script>
                </div>
                """.format(
            title_html=("<h3>{}</h3>".format(self.title) if self.title else ""),
            description_html=("<p align='left'>{}</p>".format(self.description) if self.description else ""),
            chart_id=self.graph_image_name,
            chart_id_json=json.dumps(self.graph_image_name),
            payload=json.dumps(payload),
            extra_args=extra_args,
        )

        if self.enable_csv:
            if self.yaxis_categories is not None and len(self.yaxis_categories) == len(self.data_set[0]):
                lf_csv_obj = lf_csv()
                lf_csv_obj.columns = [self.yaxis_name] + list(self.label)
                lf_csv_obj.rows = [self.yaxis_categories] + list(self.data_set)
                lf_csv_obj.filename = "{}.csv".format(self.graph_image_name)
                lf_csv_obj.generate_csv()
            else:
                raise ValueError("Length and x-axis values and y-axis values should be same.")

        return markup


class lf_line_graph:
    """Interactive multi-series line chart for use with
    lf_report.set_graph_image()/build_graph().

    Example:
        line = lf_line_graph(_data_set=[[10, 20, 30]], _xaxis_categories=["A", "B", "C"])
        report.set_graph_image(line.build_line_graph())
        report.build_graph()
    """

    def __init__(self, _data_set=None,
                 _xaxis_name="x-axis",
                 _yaxis_name="y-axis",
                 _xaxis_categories=None,
                 _xaxis_label=None,
                 _graph_title="",
                 _title_size=16,
                 _graph_image_name="line_graph",
                 _label=None,
                 _font_weight='bold',
                 _color=None,
                 _figsize=(10, 5),
                 _xaxis_step=5,
                 _xticks_font=None,
                 _text_font=None,
                 _legend_handles=None,
                 _legend_loc="best",
                 _legend_box=None,
                 _legend_ncol=1,
                 _legend_fontsize=None,
                 _marker=None,
                 _dpi=96,
                 _grid=True,
                 _enable_csv=False,
                 _reverse_x=False,
                 _reverse_y=False,
                 _dashed=None,
                 _description=""):
        """Stores the line chart data and options.

        Args:
            _data_set (list): one list of values per line.
            _xaxis_name (str): x-axis label.
            _yaxis_name (str): y-axis label.
            _xaxis_categories (list): tick values shown on the x-axis.
            _xaxis_label (list): tick text shown on the x-axis.
            _graph_title (str): chart title.
            _graph_image_name (str): chart id, and the CSV file name when _enable_csv is True.
            _label (list): one name per line, used in the legend.
            _color (list): one color per line.
            _enable_csv (bool): also save the data as a CSV file.
            _reverse_x (bool): flip the x-axis direction.
            _reverse_y (bool): flip the y-axis direction.
            _dashed (list): one True/False per line, to draw it dashed, e.g. a target line.
            _description (str): text shown under the chart title.

            Most other options (_title_size, _font_weight, _figsize, _xaxis_step,
            _xticks_font, _text_font, _legend_*, _marker, _dpi, _grid) are matplotlib-only:
            they're accepted so old callers keep working, but this interactive version
            doesn't use them.
        """
        if _data_set is None:
            _data_set = [[30.4, 55.3, 69.2, 37.1, 44.0], [45.1, 67.2, 34.3, 22.4, 37.6], [22.5, 45.6, 12.7, 34.8, 22.5]]
        if _xaxis_categories is None:
            _xaxis_categories = [1, 2, 3, 4, 5]
        if _xaxis_label is None:
            _xaxis_label = ["a", "b", "c", "d", "e"]
        if _label is None:
            _label = ["bi-downlink", "bi-uplink", 'uplink']
        if _color is None:
            # Use the brand palette by default.
            _color = list(_ECHARTS_PALETTE)
        if _marker is None:
            _marker = ['s', 'o', 'v']
        self.grid = _grid
        self.data_set = _data_set
        self.xaxis_name = _xaxis_name
        self.yaxis_name = _yaxis_name
        self.xaxis_categories = _xaxis_categories
        self.xaxis_label = _xaxis_label
        self.grp_title = _graph_title
        self.title_size = _title_size
        self.graph_image_name = _graph_image_name
        self.label = _label
        self.color = _color
        self.font_weight = _font_weight
        self.figsize = _figsize
        self.xaxis_step = _xaxis_step
        self.xticks_font = _xticks_font
        self.text_font = _text_font
        self.marker = _marker
        self.enable_csv = _enable_csv
        self.legend_handles = _legend_handles
        self.legend_loc = _legend_loc
        self.legend_box = _legend_box
        self.legend_ncol = _legend_ncol
        self.legend_fontsize = _legend_fontsize
        self.reverse_x = _reverse_x
        self.reverse_y = _reverse_y
        # Series can be drawn dashed, e.g. for a target line.
        self.dashed = _dashed or []
        self.description = _description

    def build_line_graph(self):
        """Returns the interactive line chart as HTML for set_graph_image().
        Also saves <graph_image_name>.csv when _enable_csv is True.

        Returns:
            str: chart-card HTML markup.

        Example:
            html = line.build_line_graph()
        """
        series = [
            {
                "name": self.label[i] if i < len(self.label) else "series-{}".format(i),
                "data": self.data_set[i],
                "color": _css_color(self.color[i % len(self.color)]),
                "dashed": bool(self.dashed[i]) if i < len(self.dashed) else False,
            }
            for i in range(len(self.data_set))
        ]
        payload = {
            "categories": [str(c) for c in self.xaxis_categories],
            "series": series,
            "inverseX": bool(self.reverse_x),
            "inverseY": bool(self.reverse_y),
        }
        extra_args = ", {y}, {x}".format(y=json.dumps(self.yaxis_name), x=json.dumps(self.xaxis_name))
        markup = """
                <div class='chart-card'>
                  {title_html}
                  {description_html}
                  <div id='{chart_id}' class='chart'></div>
                  <script>
                    window.__lfModernReport.renderLineChart({chart_id_json}, {payload}{extra_args});
                  </script>
                </div>
                """.format(
            title_html=("<h3>{}</h3>".format(self.grp_title) if self.grp_title else ""),
            description_html=("<p align='left'>{}</p>".format(self.description) if self.description else ""),
            chart_id=self.graph_image_name,
            chart_id_json=json.dumps(self.graph_image_name),
            payload=json.dumps(payload),
            extra_args=extra_args,
        )

        if self.enable_csv:
            if self.data_set is not None:
                lf_csv_obj = lf_csv()
                lf_csv_obj.columns = list(self.label)
                lf_csv_obj.rows = list(self.data_set)
                lf_csv_obj.filename = "{}.csv".format(self.graph_image_name)
                lf_csv_obj.generate_csv()
            else:
                logger.debug("No Dataset Found")

        return markup


class lf_pie_graph:
    """Interactive pie/donut chart for use with
    lf_report.set_graph_image()/build_graph().

    Example:
        pie = lf_pie_graph(_data_set=[70, 30], _label=["Online", "Offline"])
        report.set_graph_image(pie.build_pie_graph())
        report.build_graph()
    """

    # Counter for giving each pie chart a unique id when none is passed.
    _chart_id_counter = 0

    def __init__(self, _data_set=None,
                 _label=None,
                 _graph_title="",
                 _graph_image_name="pie_chart",
                 _subtitle="",
                 _legend=True,
                 _show_percentage=True,
                 _show_labels=True,
                 _center_label=None,
                 _tooltip_formatter=None,
                 _label_formatter=None,
                 _colors=None,
                 _item_details=None,
                 _radius=None,
                 _center=None,
                 _figsize=None,
                 _empty_message="No data available",
                 _enable_csv=False):
        """Stores the pie chart values, labels and display options.

        Args:
            _data_set (list): slice values.
            _label (list): one name per slice, parallel to _data_set.
            _graph_title (str): chart title.
            _graph_image_name (str): chart id, and the CSV file name when _enable_csv is True.
            _subtitle (str): one-line text shown under the title.
            _legend (bool): show the bottom legend.
            _show_percentage (bool): show the percent on each slice's label.
            _show_labels (bool): show the on-slice text labels at all.
            _center_label: text for the middle of the donut hole.
            _tooltip_formatter (str): custom ECharts tooltip format string.
            _label_formatter (str): custom ECharts label format string.
            _colors (list): one CSS color per slice.
            _item_details (dict): {slice_name: [detail line, ...]} shown in that slice's tooltip.
            _radius (list): inner/outer radius, e.g. ["0%", "70%"] for a solid pie.
            _center (list): [x, y] position of the chart within its box.
            _figsize (tuple): (width, height) in pixels; kept for signature parity with the
                other graph classes' matplotlib _figsize.
            _empty_message (str): message shown when there's no data to plot.
            _enable_csv (bool): also save the data as a CSV file.
        """
        if _data_set is None:
            _data_set = [30.4, 55.3, 69.2, 37.1]
        if _label is None:
            _label = ["a", "b", "c", "d"]
        self.data_set = _data_set
        self.label = _label
        self.title = _graph_title
        self.graph_image_name = _graph_image_name
        self.subtitle = _subtitle
        self.legend = _legend
        self.show_percentage = _show_percentage
        self.show_labels = _show_labels
        self.center_label = _center_label
        self.tooltip_formatter = _tooltip_formatter
        self.label_formatter = _label_formatter
        self.colors = _colors
        self.item_details = _item_details
        self.radius = _radius
        self.center = _center
        # Charts are sized by CSS; _figsize is only used when given.
        self.width, self.height = _figsize if _figsize else (None, None)
        self.empty_message = _empty_message
        self.enable_csv = _enable_csv

    def build_pie_payload(self, chart_id=None):
        """Builds the chart id and ECharts payload for this pie/donut, with no card, title,
        or legend markup around it -- for embedding inside a larger custom layout (e.g.
        lf_report.build_device_summary_card()'s stats/donut/table card). Use build_pie_graph()
        instead for a standalone chart-card section.

        Args:
            chart_id (str): DOM id for the chart container; uses graph_image_name
                (or an auto id) when left blank.

        Returns:
            tuple: (chart_id (str), payload (dict) or None). payload is None when there's no
                valid data to plot -- the caller should render its own empty-state markup
                in that case, same as renderFallback() does for build_pie_graph().

        Example:
            chart_id, payload = pie.build_pie_payload()
        """
        raw_data = [
            {"name": self.label[i] if i < len(self.label) else "series-{}".format(i), "value": v}
            for i, v in enumerate(self.data_set)
        ]
        chart_id = chart_id or self.graph_image_name
        if not chart_id:
            lf_pie_graph._chart_id_counter += 1
            chart_id = "pie-chart-{}".format(lf_pie_graph._chart_id_counter)

        # Drop bad slices and fix bad values instead of crashing.
        slices = []
        for item in raw_data:
            name = item.get("name")
            if name is None or str(name).strip() == "":
                continue
            value = item.get("value")
            if value is None:
                value = 0
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0
            if value < 0 or value != value:  # negative or NaN
                value = 0
            slices.append({"name": str(name), "value": value})
        total = sum(s["value"] for s in slices)

        if not slices or total <= 0:
            return chart_id, None

        payload = {"slices": slices, "showPercentage": bool(self.show_percentage)}
        if not self.legend:
            payload["legend"] = False
        if not self.show_labels:
            payload["showLabels"] = False
        if self.center_label is not None:
            payload["centerLabel"] = self.center_label
        if self.tooltip_formatter:
            payload["tooltipFormatter"] = self.tooltip_formatter
        if self.label_formatter:
            payload["labelFormatter"] = self.label_formatter
        if self.colors:
            payload["colors"] = list(self.colors)
        if self.item_details:
            payload["itemDetails"] = self.item_details
        if self.radius:
            payload["radius"] = list(self.radius)
        if self.center:
            payload["center"] = list(self.center)
        return chart_id, payload

    def build_pie_graph(self):
        """Returns the interactive pie chart as HTML for set_graph_image().
        Also saves <graph_image_name>.csv when _enable_csv is True.

        Returns:
            str: chart-card HTML markup.

        Example:
            html = pie.build_pie_graph()
        """
        chart_id, payload = self.build_pie_payload()

        title_html = "<h3>{}</h3>".format(self.title) if self.title else ""
        subtitle_html = "<p class='chart-subtitle'>{}</p>".format(self.subtitle) if self.subtitle else ""

        if payload is None:
            # No data: show a message instead of an empty chart.
            markup = """
                <div class='chart-card'>
                  {title_html}
                  {subtitle_html}
                  <div id='{chart_id}' class='chart'>
                    <div class='chart-fallback'>{message}</div>
                  </div>
                </div>
                """.format(
                title_html=title_html,
                subtitle_html=subtitle_html,
                chart_id=chart_id,
                message=self.empty_message,
            )
        else:
            style_parts = []
            if self.width:
                style_parts.append("width:{}".format(self.width if isinstance(self.width, str) else "{}px".format(self.width)))
            if self.height:
                style_parts.append("height:{}".format(self.height if isinstance(self.height, str) else "{}px".format(self.height)))
            container_style = " style='{}'".format(";".join(style_parts)) if style_parts else ""

            markup = """
                <div class='chart-card'>
                  {title_html}
                  {subtitle_html}
                  <div id='{chart_id}' class='chart'{container_style}></div>
                  <script>
                    window.__lfModernReport.renderPieChart({chart_id_json}, {payload});
                  </script>
                </div>
                """.format(
                title_html=title_html,
                subtitle_html=subtitle_html,
                chart_id=chart_id,
                container_style=container_style,
                chart_id_json=json.dumps(chart_id),
                payload=json.dumps(payload),
            )

        if self.enable_csv:
            lf_csv_obj = lf_csv()
            lf_csv_obj.columns = list(self.label)
            lf_csv_obj.rows = [self.data_set]
            lf_csv_obj.filename = "{}.csv".format(self.graph_image_name)
            lf_csv_obj.generate_csv()

        return markup
