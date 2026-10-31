#!/usr/bin/env python3
"""
NAME: lf_report_v2.py

PURPOSE:

- A newer version of lf_report.py. The `lf_report` class works the same way,
  so existing scripts only need to change the import.
- Builds HTML and PDF reports with a modern look (artifacts/report_v2.css)
  and interactive charts using ECharts (artifacts/echarts.min.js).
- Old PNG charts from lf_graph.py still work; they are shown in the new style.
- The interactive chart classes (lf_bar_graph, lf_bar_graph_horizontal,
  lf_line_graph, lf_pie_graph) are in lf_graph_v2.py.

EXAMPLE:
    from report_v2.lf_report_v2 import lf_report

    report = lf_report(_title="My Test Report")
    report.build_banner()
    report.set_table_dataframe(dataframe)
    report.build_table()
    report.build_footer()
    report.write_html()
    report.write_pdf()

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright (C) 2020-2026 Candela Technologies Inc

INCLUDE_IN_README
"""
# CAUTION: adding imports to this file which are not in update_dependencies.py is not advised
import argparse
import base64
import datetime
import importlib
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

# The PDF worker does not need the report-building libraries.
_IS_PDF_WORKER = __name__ == '__main__' and '--pdf-worker' in sys.argv[1:]
if not _IS_PDF_WORKER:
    import pandas as pd
    import pdfkit

if not _IS_PDF_WORKER:
    # Support both package imports and direct execution of this implementation.
    _py_scripts_dir = Path(__file__).resolve().parent.parent
    _repo_root = _py_scripts_dir.parent
    for _import_root in (_py_scripts_dir, _repo_root):
        if str(_import_root) not in sys.path:
            sys.path.append(str(_import_root))

    logger = logging.getLogger(__name__)
    lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
    lf_csv = importlib.import_module("py-scripts.lf_csv").lf_csv
    lf_pie_graph = importlib.import_module("report_v2.lf_graph_v2").lf_pie_graph
    os_name = platform.system()

__all__ = ["lf_report"]


def _configure_playwright_browser_path():
    """Set and return the persistent directory used for Playwright browsers."""
    configured = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
    if configured == '0':
        raise RuntimeError('Use a persistent directory for PLAYWRIGHT_BROWSERS_PATH, not 0')
    browser_dir = Path(configured).expanduser().resolve() if configured else (
        Path.home() / '.cache' / 'lanforge' / 'report-browsers')
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(browser_dir)
    return browser_dir


def ensure_dependencies(playwright=None):
    """Locates the Chromium browser playwright needs for PDF export. Installed by
    update_dependencies.py's install_playwright_browser() (the playwright pip
    package alone doesn't include the browser binary) -- this only locates it,
    it doesn't install anything.

    Returns:
        str: path to the Chromium executable.

    Example:
        chromium_path = ensure_dependencies()
    """
    _configure_playwright_browser_path()
    if playwright is None:
        sync_playwright = importlib.import_module('playwright.sync_api').sync_playwright
        with sync_playwright() as started_playwright:
            return ensure_dependencies(started_playwright)

    override = os.environ.get('LF_REPORT_CHROMIUM_EXECUTABLE')
    executable = Path(override).expanduser().resolve() if override else Path(playwright.chromium.executable_path)
    if not executable.is_file():
        raise RuntimeError(
            f'Chromium not found at {executable}. Run update_dependencies.py to install PDF export '
            'dependencies (or set LF_REPORT_CHROMIUM_EXECUTABLE to point at an existing Chromium).')
    return str(executable)


def export_pdf(source, destination, page_size='A4', orientation='Portrait', page_width=None, page_height=None):
    """Render a saved HTML report with headless Chromium.

    Args:
        source (str): path to the report HTML file to render.
        destination (str): path the PDF should be written to.
        page_size (str): one of 'A4', 'A3', 'Letter', 'Legal'. Ignored when page_width/page_height are set.
        orientation (str): 'Portrait' or 'Landscape'.
        page_width (str): custom page width, e.g. '210mm'. Requires page_height to also be set.
        page_height (str): custom page height, e.g. '297mm'. Requires page_width to also be set.

    Example:
        export_pdf("outfile.html", "outfile.pdf", page_size="A4", orientation="Landscape")
    """
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if orientation.lower() not in ('portrait', 'landscape'):
        raise ValueError('PDF orientation must be Portrait or Landscape')
    if (page_width is None) != (page_height is None):
        raise ValueError('Custom PDF size requires both page width and height')
    custom_mm = None
    if page_width is not None:
        dimensions = (page_width, page_height)
        if any(not isinstance(value, str) or not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?mm', value)
               for value in dimensions):
            raise ValueError('Custom PDF dimensions must be positive values in mm')
        custom_mm = tuple(float(value[:-2]) for value in dimensions)
        if min(custom_mm) <= 0:
            raise ValueError('Custom PDF dimensions must be positive values in mm')
    _configure_playwright_browser_path()
    sync_playwright = importlib.import_module('playwright.sync_api').sync_playwright
    descriptor, temporary = tempfile.mkstemp(suffix='.pdf', dir=destination.parent)
    os.close(descriptor)
    try:
        with sync_playwright() as playwright:
            executable = ensure_dependencies(playwright)
            try:
                browser = playwright.chromium.launch(executable_path=executable)
            except Exception as exc:
                raise RuntimeError(
                    "Chromium is installed but could not launch. System libraries, browser permissions, "
                    "or sandbox restrictions may need administrator setup. On supported Linux systems, "
                    "ask the administrator to run this Python environment's `python -m playwright "
                    "install-deps chromium`. No sudo or system-package installation was attempted.\n"
                    + str(exc)) from exc
            try:
                page = browser.new_page(viewport={'width': 1100 if orientation.lower() == 'landscape' else 760, 'height': 900})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.add_init_script('window.__lfReportPdf = true;')
                page.emulate_media(media='print')
                page.goto(source.as_uri(), wait_until='load', timeout=60000)
                paper_mm = {'A4': (210, 297), 'A3': (297, 420), 'Letter': (215.9, 279.4),
                            'Legal': (215.9, 355.6)}.get(page_size)
                if custom_mm:
                    paper_mm = custom_mm if orientation.lower() == 'portrait' else custom_mm[::-1]
                if paper_mm:
                    width = (paper_mm[0] if custom_mm else
                             paper_mm[1 if orientation.lower() == 'landscape' else 0]) - 20
                    page.add_style_tag(content='@media print { .report-shell { width: ' + str(width) + 'mm; } }')
                compact_height = '80mm' if orientation.lower() == 'landscape' else '95mm'
                page.add_style_tag(content='@media print { :root { --pdf-chart-height: ' + compact_height + '; } }')
                page.evaluate('''async () => {
                    await document.fonts.ready;
                    await Promise.all(Array.from(document.images).map(image => {
                        if (image.complete) {
                            if (!image.naturalWidth) throw new Error('Missing image: ' + image.src.slice(0, 160));
                            return;
                        }
                        return new Promise((resolve, reject) => {
                            image.onload = resolve;
                            image.onerror = () => reject(new Error('Image failed: ' + image.src.slice(0, 160)));
                        });
                    }));
                    document.querySelectorAll('.view-all-btn').forEach(button => button.click());
                    document.querySelectorAll('.table-search-input').forEach(input => {
                        input.value = ''; input.dispatchEvent(new Event('input'));
                    });
                    // Use rendered width, not column count, to decide whether to split.
                    for (const table of document.querySelectorAll('table.data-table, table.device-table')) {
                        const shell = table.closest('.report-shell');
                        const container = table.parentElement;
                        const available = Math.min(container.clientWidth,
                            shell ? shell.clientWidth : document.documentElement.clientWidth);
                        const fits = candidate => candidate.getBoundingClientRect().width <= available + 1 &&
                            candidate.scrollWidth <= available + 1;
                        if (fits(table)) continue;
                        table.classList.add('pdf-table-compact');
                        if (fits(table)) continue;
                        table.classList.add('pdf-table-small');
                        if (fits(table)) continue;
                        const rows = Array.from(table.rows);
                        const count = rows.length ? rows[0].cells.length : 0;
                        if (count < 2 || table.querySelector('colgroup') || rows.some(row => row.cells.length !== count ||
                            Array.from(row.cells).some(cell => cell.colSpan !== 1 || cell.rowSpan !== 1))) {
                            throw new Error('Custom table still exceeds printable width; use a larger page or adjust its layout');
                        }
                        const headers = Array.from(rows[0].cells).map(cell => cell.textContent.trim());
                        const identifier = headers.findIndex(label => /^(device name|wireless client|client|station|hostname)$/i.test(label));
                        const key = identifier >= 0 ? identifier : 0;
                        const columns = Array.from({length: count}, (_, index) => index).filter(index => index !== key);
                        const makePanel = selected => {
                            const copy = table.cloneNode(true);
                            copy.removeAttribute('id');
                            copy.style.width = '100%';
                            copy.style.minWidth = '0';
                            copy.style.tableLayout = 'auto';
                            for (const row of copy.rows) {
                                Array.from(row.cells).forEach((cell, index) => {
                                    if (index !== key && !selected.includes(index)) cell.remove();
                                });
                            }
                            container.insertBefore(copy, table);
                            return copy;
                        };
                        let start = 0;
                        while (start < columns.length) {
                            let end = start + 1;
                            let panel = makePanel(columns.slice(start, end));
                            if (!fits(panel)) {
                                panel.remove();
                                throw new Error('Table identifier and one column exceed printable width; use a larger page');
                            }
                            while (end < columns.length) {
                                const trial = makePanel(columns.slice(start, end + 1));
                                if (!fits(trial)) { trial.remove(); break; }
                                panel.remove();
                                panel = trial;
                                end++;
                            }
                            if (start > 0) {
                                const caption = panel.createCaption();
                                caption.textContent += ' Continued — additional columns';
                            }
                            start = end;
                        }
                        table.remove();
                    }
                    const charts = Array.from(document.querySelectorAll('.chart, .device-donut'));
                    for (const element of charts) {
                        const chart = window.echarts && echarts.getInstanceByDom(element);
                        if (!chart) {
                            if (!element.querySelector('.chart-fallback')) throw new Error('Chart not rendered: ' + element.id);
                            continue;
                        }
                        const option = chart.getOption();
                        option.animation = false;
                        option.dataZoom = [];
                        // Line/bar charts use a compact height in the PDF; category charts keep full height.
                        const hasClientAxis = option.yAxis && option.yAxis.some(axis => axis.type === 'category');
                        if (element.classList.contains('chart') && !hasClientAxis &&
                            option.series.every(series => series.type === 'line' || series.type === 'bar')) {
                            element.classList.add('pdf-compact-chart');
                            if (option.grid) option.grid.forEach(grid => {
                                grid.top = Math.min(Number(grid.top) || 48, 28);
                                // Leave extra room for rotated clock labels where explicitly requested.
                                grid.bottom = Math.min(Number(grid.bottom) || 84, 90);
                            });
                        }
                        if (option.legend) option.legend.forEach(legend => { legend.selected = {}; });
                        if (option.yAxis) option.yAxis.forEach(axis => {
                            if (axis.type === 'category') axis.axisLabel = Object.assign({}, axis.axisLabel,
                                {formatter: null, overflow: 'break', width: 190});
                        });
                        // Split category charts into readable page-sized panels.
                        const categoryAxis = option.yAxis && option.yAxis.find(axis => axis.type === 'category');
                        const categories = categoryAxis && categoryAxis.data;
                        const panelSize = 8;
                        if (categories && categories.length > panelSize) {
                            const card = element.closest('.chart-card');
                            if (!card) throw new Error('Oversized chart has no card: ' + element.id);
                            for (let start = 0; start < categories.length; start += panelSize) {
                                const panel = card.cloneNode(true);
                                panel.querySelectorAll('script').forEach(script => script.remove());
                                const target = panel.querySelector('.chart');
                                target.innerHTML = '';
                                target.removeAttribute('_echarts_instance_');
                                target.id = element.id + '-pdf-' + start;
                                target.style.height = '410px';
                                const heading = panel.querySelector('h3');
                                if (heading && start) heading.textContent += ' (continued)';
                                card.parentNode.insertBefore(panel, card);
                                const panelOption = Object.assign({}, option);
                                panelOption.yAxis = option.yAxis.map(axis => axis === categoryAxis
                                    ? Object.assign({}, axis, {data: categories.slice(start, start + panelSize)}) : axis);
                                panelOption.series = option.series.map(series => Object.assign({}, series, {
                                    data: series.type === 'custom'
                                        ? series.data.filter(point => point[0] >= start && point[0] < start + panelSize)
                                            .map(point => [point[0] - start, ...point.slice(1)])
                                        : series.data.slice(start, start + panelSize)
                                }));
                                echarts.init(target, null, {renderer: 'svg'}).setOption(panelOption);
                            }
                            chart.dispose();
                            card.remove();
                        } else {
                            chart.setOption(option, true);
                            chart.resize();
                        }
                    }
                    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
                }''')
                if errors:
                    raise RuntimeError('Report JavaScript errors: ' + '; '.join(errors))
                # Flow content avoids empty header/footer bands on intermediate pages.
                pdf_options = dict(format=page_size, landscape=orientation.lower() == 'landscape',
                                   print_background=True,
                                   margin={'top': '10mm', 'bottom': '10mm', 'left': '10mm', 'right': '10mm'},
                                   display_header_footer=False)
                if custom_mm:
                    pdf_options.pop('format')
                    pdf_options.update(width=f'{paper_mm[0]}mm', height=f'{paper_mm[1]}mm', landscape=False)
                Path(temporary).write_bytes(page.pdf(**pdf_options))
            finally:
                browser.close()
        if Path(temporary).stat().st_size < 100 or Path(temporary).read_bytes()[:5] != b'%PDF-':
            raise RuntimeError('PDF export produced an invalid file')
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _run_pdf_worker():
    """Parse the isolated PDF worker command line and export the report.

    Example:
        python lf_report_v2.py --pdf-worker outfile.html outfile.pdf --page-size A4
    """
    parser = argparse.ArgumentParser(description='Export saved report HTML to PDF')
    parser.add_argument('--pdf-worker', action='store_true')
    parser.add_argument('source')
    parser.add_argument('destination')
    parser.add_argument('--page-size', default='A4')
    parser.add_argument('--orientation', default='Portrait')
    parser.add_argument('--page-width')
    parser.add_argument('--page-height')
    args = parser.parse_args()
    export_pdf(args.source, args.destination, args.page_size, args.orientation, args.page_width, args.page_height)


class lf_report:
    """Builds a LANforge HTML/PDF test report piece by piece (banner, text, tables, charts, footer).
    Same API as the old lf_report.py; only the look is modernized.

    Example:
        report = lf_report(_title="My Test Report")
        report.build_banner()
        report.build_footer()
        report.write_html()
        report.write_pdf()
    """
    # Score band -> (label, color): Excellent 90-100, Good 80-89, Average 70-79, Poor <70.
    SCORE_RATING_BANDS = [(90, "Excellent", "#1e7e34"), (80, "Good", "#28a745"),
                          (70, "Average", "#f1c40f"), (0, "Poor", "#e74c3c")]

    @classmethod
    def classify_score_rating(cls, score):
        """Maps a numeric score to a rating label and color (Excellent/Good/Average/Poor).

        Args:
            score (float): score to classify, 0-100.

        Returns:
            tuple: (label (str), color (str)) for the band the score falls in.

        Example:
            label, color = lf_report.classify_score_rating(85)
        """
        for threshold, label, color in cls.SCORE_RATING_BANDS:
            if score >= threshold:
                return label, color
        return cls.SCORE_RATING_BANDS[-1][1], cls.SCORE_RATING_BANDS[-1][2]

    def __init__(self,
                 # _path the report directory under which the report directories will be created.
                 _path="/home/lanforge/html-reports",
                 _alt_path="",
                 _date="",
                 _title="LANForge Unit Test Run Heading",
                 _table_title="LANForge Table Heading",
                 _graph_title="LANForge Graph Title",
                 _obj="",
                 _obj_title="",
                 _output_html="outfile.html",
                 _output_pdf="outfile.pdf",
                 _results_dir_name="LANforge_Test_Results_Unit_Test",
                 _output_format='html',  # pass in on the write functionality, current not used
                 _dataframe="",
                 _path_date_time="",
                 _custom_css=None):  # this is where the final report is placed.
        """Sets up the report and creates its '<date>_<results_dir_name>' folder under _path.
        Also copies the CSS, logos, font and chart script into that folder.

        Args:
            _path (str): base folder the report folder is created under ("local"/"here" uses
                this script's own folder instead).
            _alt_path (str): if set, used as the base folder instead of _path.
            _date (str): report date; current date/time is used when empty.
            _title (str): report title shown in the banner.
            _table_title (str): heading used by the first build_table_title() call.
            _graph_title (str): heading used by the first build_graph_title() call.
            _obj (str): objective text used by build_objective().
            _obj_title (str): objective heading used by build_objective().
            _output_html (str): HTML file name written by write_html().
            _output_pdf (str): PDF file name written by write_pdf().
            _results_dir_name (str): second half of the report folder name.
            _output_format (str): accepted for compatibility; not currently used.
            _dataframe: initial table (pandas DataFrame) for build_table().
            _path_date_time (str): pre-set report folder path; normally left empty and computed.
            _custom_css (str): optional custom CSS file (from the artifacts folder), copied in as custom.css.

        Example:
            report = lf_report(_path="/home/lanforge/html-reports", _title="My Test Report",
                                _results_dir_name="LANforge_Test_Results")
        """
        # other report paths,

        # _path is where the directory with the data time will be created
        if _path == "local" or _path == "here":
            self.path = os.path.abspath(__file__)
            logger.info("path set to file path: {}".format(self.path))
        elif _alt_path != "":
            self.path = _alt_path
            logger.info("path set to alt path: {}".format(self.path))
        else:
            self.path = _path
            logger.info("path set: {}".format(self.path))

        self.dataframe = _dataframe
        self.text = ""
        self.title = _title
        self.table_title = _table_title
        self.graph_title = _graph_title
        self.date = _date
        self.output_html = _output_html
        if _output_html.lower().endswith(".pdf"):
            raise ValueError("HTML output file cannot end with suffix '.pdf'")
        self.path_date_time = _path_date_time
        self.report_location = ""   # used by lf_check.py to know where to write the meta data "Report Location:::/home/lanforge/html-reports/wifi-capacity-2021-08-17-04-02-56"
        self.write_output_html = ""
        self.write_output_index_html = ""
        self.output_pdf = _output_pdf
        self.write_output_pdf = ""
        self.banner_html = ""
        self.footer_html = ""
        self.graph_titles = ""
        self.graph_image = ""
        self.csv_file_name = ""
        self.html = ""
        self.custom_html = ""
        self.pdf_link_html = ""
        self.objective = _obj
        self.obj_title = _obj_title
        self.description = ""
        self.desc_title = ""
        self.date_time_directory = ""
        self.log_directory = ""

        self.banner_directory = "artifacts"
        self.banner_file_name = "banner.png"
        self.logo_directory = "artifacts"
        self.logo_file_name = "yellow.png"
        self.logo_footer_file_name = "candela_swirl_small-72h.png"
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.custom_css = _custom_css
        # modern report assets
        self.modern_css_file = "report_v2.css"
        self.echarts_file = "echarts.min.js"
        self._echarts_palette = ["#2a78d6", "#d0662a", "#1a9fb4", "#7650c8", "#b03a7d", "#5a6fd1"]
        # Counter for giving each device summary card a unique id when none is passed.
        self._chart_id_counter = 0
        self._finding_type_icon = {"positive": "&#10003;", "neutral": "&bull;", "warning": "&#9888;", "critical": "&#10007;"}
        # Inline artwork keeps platform badges available in offline HTML and PDF reports.
        platform_icon_shapes = {
            "Android": '<g fill="#3d9b35"><path d="M5 10a7 7 0 0 1 14 0Z"/>'
                       '<rect x="5" y="11" width="14" height="8" rx="2"/>'
                       '<path d="M7 18h3v4H7zm7 0h3v4h-3z"/>'
                       '<rect x="1" y="10" width="3" height="9" rx="1.5"/>'
                       '<rect x="20" y="10" width="3" height="9" rx="1.5"/></g>'
                       '<path d="m7 4-2-3m12 3 2-3" stroke="#3d9b35" stroke-linecap="round"/>'
                       '<g fill="white"><circle cx="9" cy="7" r="1"/><circle cx="15" cy="7" r="1"/></g>',
            "Windows": '<path fill="#0078d4" d="M2 4 11 2.8V11H2Zm11-1.5L22 1v10h-9Z'
                       'M2 13h9v8.2L2 20Zm11 0h9v10l-9-1.5Z"/>',
            "Linux": '<path fill="#202938" d="M7 10V7a5 5 0 0 1 10 0v3l4 9-5 2H8l-5-2Z"/>'
                     '<ellipse cx="12" cy="15" rx="5" ry="6" fill="white"/>'
                     '<g fill="white"><ellipse cx="10" cy="7" rx="1.5" ry="2"/>'
                     '<ellipse cx="14" cy="7" rx="1.5" ry="2"/></g>'
                     '<g fill="#202938"><circle cx="10.5" cy="7" r=".7"/>'
                     '<circle cx="13.5" cy="7" r=".7"/></g>'
                     '<path fill="#f5b522" d="m9 10 3-2 3 2-3 2ZM2 20l5-2 3 4H2Zm12 2 3-4 5 2v2Z"/>',
            "macOS": '<path fill="#374151" d="M16.8 1c.2 2-1.4 4-3.5 4.2C13 3.3 14.7 1.3 16.8 1Z'
                     'M20.5 7.5c-1.1-1.6-2.7-2.3-4.2-2.3-1.8 0-2.7 1-4.1 1-1.3 0-2.4-1-4-1'
                     'C5.4 5.2 3 7.6 3 11.3c0 4.7 3.3 10.7 6 10.7 1.5 0 2.1-.9 3.8-.9'
                     's2.1.9 3.7.9c2 0 4-3.4 4.8-5.5-4.1-1.7-4.7-6.5-.8-9Z"/>',
            "iOS": '<rect x="7" y="1" width="10" height="22" rx="2.2" fill="#374151"/>'
                   '<rect x="7.9" y="3.3" width="8.2" height="16.6" fill="white"/>'
                   '<circle cx="12" cy="20.7" r="1" fill="#374151"/>',
        }
        self._platform_icons = {
            name.lower(): '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
                          'width="24" height="24" style="width:24px;height:24px;display:block" '
                          'aria-hidden="true" focusable="false">' + shapes + '</svg>'
            for name, shapes in platform_icon_shapes.items()
        }
        self._platform_icons.update(dict.fromkeys(("mac", "mac os", "mac os x", "osx", "darwin", "macbook"),
                                                  self._platform_icons["macos"]))
        self._platform_icons.update(dict.fromkeys(("win", "win32", "win64"), self._platform_icons["windows"]))
        self._chart_markup_sentinel = "<div class='chart-card'>"

        # note: the following 3 calls must be in order
        self.set_date_time_directory(_date, _results_dir_name)
        self.build_date_time_directory()
        self.build_log_directory()

        self.font_file = "CenturyGothic.woff"
        # move the banners and candela images to report path
        self.copy_banner()
        self.copy_css()
        self.copy_logo()
        self.copy_logo_footer()
        self.copy_echarts()

    def copy_banner(self):
        """Copies the banner image into the report folder.

        Example:
            report.copy_banner()
        """
        banner_src_file = str(self.current_path) + '/' + str(self.banner_directory) + '/' + str(self.banner_file_name)
        banner_dst_file = str(self.path_date_time) + '/' + str(self.banner_file_name)
        shutil.copy(banner_src_file, banner_dst_file)

    def copy_css(self):
        """Copies the stylesheet (saved as report.css), custom.css and the report font into the report folder.

        Example:
            report.copy_css()
        """
        # modern report stylesheet is copied to the same output filename ("report.css")
        reportcss_src_file = str(self.current_path) + '/' + str(self.banner_directory) + '/' + str(self.modern_css_file)
        reportcss_dest_file = str(self.path_date_time) + '/report.css'

        font_src_file = str(self.current_path) + '/' + str(self.banner_directory) + '/' + str(self.font_file)
        font_dest_file = str(self.path_date_time) + '/' + str(self.font_file)

        shutil.copy(reportcss_src_file, reportcss_dest_file)
        if self.custom_css:
            customcss_src_file = str(self.current_path) + '/' + str(self.banner_directory) + '/' + str(self.custom_css)
            customcss_dest_file = str(self.path_date_time) + '/custom.css'
            shutil.copy(customcss_src_file, customcss_dest_file)
        shutil.copy(font_src_file, font_dest_file)

    def copy_echarts(self):
        """Copies the ECharts library (used by the interactive charts) into the report folder.

        Example:
            report.copy_echarts()
        """
        echarts_src_file = str(self.current_path) + '/' + str(self.banner_directory) + '/' + str(self.echarts_file)
        echarts_dst_file = str(self.path_date_time) + '/' + str(self.echarts_file)
        shutil.copy(echarts_src_file, echarts_dst_file)

    def copy_logo(self):
        """Copies the header logo into the report folder.

        Example:
            report.copy_logo()
        """
        logo_src_file = str(self.current_path) + '/' + str(self.logo_directory) + '/' + str(self.logo_file_name)
        logo_dst_file = str(self.path_date_time) + '/' + str(self.logo_file_name)
        shutil.copy(logo_src_file, logo_dst_file)

    def copy_logo_footer(self):
        """Copies the small footer logo into the report folder.

        Example:
            report.copy_logo_footer()
        """
        logo_footer_src_file = str(self.current_path) + '/' + str(self.logo_directory) + '/' + str(
            self.logo_footer_file_name)
        logo_footer_dst_file = str(self.path_date_time) + '/' + str(self.logo_footer_file_name)
        shutil.copy(logo_footer_src_file, logo_footer_dst_file)

    def move_graph_image(self, ):
        """Moves the current graph PNG into the report folder.
        Does nothing for interactive charts, since those are HTML and not a file.

        Example:
            report.move_graph_image()
        """
        if self._chart_markup_sentinel in str(self.graph_image):
            # Interactive chart markup, not a PNG file: nothing to move.
            return
        graph_src_file = str(self.graph_image)
        graph_dst_file = str(self.path_date_time) + '/' + str(self.graph_image)
        logger.info("graph_src_file: {}".format(graph_src_file))
        logger.info("graph_dst_file: {}".format(graph_dst_file))
        shutil.move(graph_src_file, graph_dst_file)

    def move_csv_file(self):
        """Moves the current CSV file (set by set_csv_filename) into the report folder.

        Example:
            report.move_csv_file()
        """
        csv_src_file = str(self.csv_file_name)
        csv_dst_file = str(self.path_date_time) + '/' + str(self.csv_file_name)
        logger.info("csv_src_file: {}".format(csv_src_file))
        logger.info("csv_dst_file: {}".format(csv_dst_file))
        shutil.move(csv_src_file, csv_dst_file)

    def set_date_time_directory(self, _date, _results_dir_name):
        """Decides the report folder name: '<date>_<results_dir_name>'.
        Uses the current date and time when no date is given.

        Args:
            _date (str): date string to use; current date/time is used when empty.
            _results_dir_name (str): second half of the report folder name.

        Example:
            report.set_date_time_directory("2026-01-01-12-00-00", "LANforge_Test_Results")
        """
        self.date = _date
        self.results_dir_name = _results_dir_name
        if self.date != "":
            self.date_time_directory = str(self.date) + str("_") + str(self.results_dir_name)
        else:
            self.date = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")).replace(':', '-')
            self.date_time_directory = self.date + str("_") + str(self.results_dir_name)

    def build_date_time_directory(self):
        """Creates the report folder on disk.
        Falls back to a folder next to this script if the path can't be created.

        Example:
            report.build_date_time_directory()
        """
        if self.date_time_directory == "":
            self.set_date_time_directory()
        self.path_date_time = os.path.join(self.path, self.date_time_directory)
        logger.info("path_date_time {}".format(self.path_date_time))
        try:
            if not os.path.exists(self.path_date_time):
                os.mkdir(self.path_date_time)
        except Exception as x:
            traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            self.path_date_time = os.path.join(self.current_path, self.date_time_directory)
            if not os.path.exists(self.path_date_time):
                os.mkdir(self.path_date_time)
        logger.info("report path : {}".format(self.path_date_time))

    def build_log_directory(self):
        """Creates the 'log' sub-folder inside the report folder; exits if that fails.

        Example:
            report.build_log_directory()
        """
        if self.log_directory == "":
            self.log_directory = os.path.join(self.path_date_time, "log")
        try:
            if not os.path.exists(self.log_directory):
                os.mkdir(self.log_directory)
        except Exception as x:
            traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            logger.critical("exception making {}".format(self.log_directory))
            exit(1)

    def set_title(self, _title):
        """Sets the report title shown in the banner.

        Args:
            _title (str): report title.

        Example:
            report.set_title("My Test Report")
        """
        self.title = _title

    def set_table_title(self, _table_title):
        """Sets the heading used by the next build_table_title() call.

        Args:
            _table_title (str): table heading.

        Example:
            report.set_table_title("Station Results")
        """
        self.table_title = _table_title

    # sets the csv file name as graph title
    def set_csv_filename(self, _graph_title):
        """Sets the CSV file name to the graph name with a .csv extension.

        Args:
            _graph_title (str): name to base the CSV file name on.

        Example:
            report.set_csv_filename("throughput-graph")
        """
        fname, ext = os.path.splitext(_graph_title)
        self.csv_file_name = fname + ".csv"

    def set_table_dataframe(self, _dataframe):
        """Sets the table (pandas DataFrame) used by the next build_table() call.

        Args:
            _dataframe (DataFrame): table to store.

        Example:
            report.set_table_dataframe(dataframe)
        """
        self.dataframe = _dataframe

    def set_custom_html(self, _custom_html):
        """Sets raw HTML to add with the next build_custom() call.

        Args:
            _custom_html (str): raw HTML to store.

        Example:
            report.set_custom_html("<p>Custom section</p>")
        """
        self.custom_html = _custom_html

    def set_obj_html(self, _obj_title, _obj):
        """Sets the heading and text for the next build_objective() section.

        Args:
            _obj_title (str): objective heading.
            _obj (str): objective body text.

        Example:
            report.set_obj_html("Objective", "Verify throughput under load.")
        """
        self.objective = _obj
        self.obj_title = _obj_title

    def set_graph_image(self, _graph_image):
        """Sets the graph (a PNG path or interactive chart HTML) used by the next build_graph() call.

        Args:
            _graph_image (str): PNG file path, or interactive chart HTML.

        Example:
            report.set_graph_image("throughput.png")
        """
        self.graph_image = _graph_image

    def write_html(self):
        """Writes the report HTML to the report folder and returns the file path.

        Returns:
            str: full path to the written HTML file, or None if no HTML file name was set.

        Example:
            html_file = report.write_html()
        """
        if not self.output_html:
            logger.info("no html file name, skipping report generation")
            return
        if self.output_html.lower().endswith(".pdf"):
            raise ValueError("write_html: HTML filename [%s] should not end with .pdf" % self.output_html)
        if self.write_output_html.endswith(".pdf"):
            raise ValueError("wrong suffix for an HTML file: %s" % self.write_output_html)
        self.write_output_html = str(self.path_date_time) + '/' + str(self.output_html)
        logger.info("write_output_html: {}".format(self.write_output_html))
        try:
            test_file = open(self.write_output_html, "w")
            test_file.write(self.html)
            test_file.close()
        except Exception as x:
            traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            logger.info("write_html failed")
        return self.write_output_html

    @staticmethod
    def _write_pdf_file(input_html, output_pdf, options, configuration=None):
        """Export HTML through Chromium or the legacy wkhtmltopdf backend.

        Args:
            input_html (str): path to the source HTML report.
            output_pdf (str): path the PDF should be written to.
            options (dict): PDF options from _pdf_options(), or wkhtmltopdf-style options.
            configuration: optional pdfkit.configuration() object (wkhtmltopdf backend only).

        Example:
            lf_report._write_pdf_file("outfile.html", "outfile.pdf", {"page-size": "A4", "orientation": "Portrait"})
        """
        backend = os.environ.get("LF_REPORT_PDF_BACKEND", "chromium").lower()
        if backend == "chromium":
            worker = os.path.abspath(__file__)
            dimension_args = []
            for key in ("page-width", "page-height"):
                if key in options:
                    dimension_args.extend(["--" + key, options[key]])
            result = subprocess.run(
                [sys.executable, worker, "--pdf-worker", os.path.abspath(input_html), os.path.abspath(output_pdf),
                 "--page-size", options.get("page-size", "A4"),
                 "--orientation", options.get("orientation", "Portrait")] + dimension_args,
                capture_output=True, text=True, timeout=2400)
            if result.returncode:
                raise RuntimeError("Chromium PDF export failed; HTML is preserved. Install "
                                   "the pinned Playwright dependency from update_dependencies.py and its matching Chromium browser. "
                                   "Check PLAYWRIGHT_BROWSERS_PATH / LF_REPORT_CHROMIUM_EXECUTABLE.\n"
                                   + result.stderr[-6000:])
            return
        if backend != "wkhtmltopdf":
            raise ValueError("LF_REPORT_PDF_BACKEND must be chromium or wkhtmltopdf")
        logger.warning("Using legacy wkhtmltopdf: interactive charts and layout may be incomplete")
        kwargs = {'options': options}
        if configuration is not None:
            kwargs['configuration'] = configuration

        try:
            pdfkit.from_file(input_html, output_pdf, **kwargs)
        except OSError as error:
            # wkhtmltopdf sometimes crashes once with -11; retry.
            if 'non-zero code -11' not in str(error):
                raise
            logger.warning('wkhtmltopdf crashed with exit code -11; retrying PDF generation once')
            pdfkit.from_file(input_html, output_pdf, **kwargs)

    @staticmethod
    def _pdf_options(page_size, orientation, page_width, page_height):
        """Build options shared by both PDF output methods.

        Args:
            page_size (str): one of 'A4', 'A3', 'Letter', 'Legal'. Ignored when page_width/page_height are set.
            orientation (str): 'Portrait' or 'Landscape'.
            page_width (str): custom page width, e.g. '210mm'. Requires page_height to also be set.
            page_height (str): custom page height, e.g. '297mm'. Requires page_width to also be set.

        Returns:
            dict: options for pdfkit/the Chromium worker.

        Example:
            options = lf_report._pdf_options("A4", "Portrait", None, None)
        """
        if (page_width is None) != (page_height is None):
            raise ValueError('Custom PDF size requires both page width and height')
        options = {'enable-local-file-access': None, 'orientation': orientation}
        if page_width is None:
            options['page-size'] = page_size
        else:
            options.update({'page-width': page_width, 'page-height': page_height})
        return options

    def write_pdf(self, _page_size='A4', _orientation='Portrait', _page_width=None, _page_height=None):
        """Write the report PDF to the report folder.

        Args:
            _page_size (str): one of 'A4', 'A3', 'Letter', 'Legal'. Ignored when _page_width/_page_height are set.
            _orientation (str): 'Portrait' or 'Landscape'.
            _page_width (str): custom page width, e.g. '210mm'. Requires _page_height to also be set.
            _page_height (str): custom page height, e.g. '297mm'. Requires _page_width to also be set.

        Example:
            report.write_pdf(_page_size="A4", _orientation="Landscape")
        """
        if not self.output_pdf:
            logger.info("write_pdf: no pdf file name, skipping pdf output")
            return
        options = self._pdf_options(_page_size, _orientation, _page_width, _page_height)
        self.write_output_pdf = str(self.path_date_time) + '/' + str(self.output_pdf)
        if os_name == "Windows" and os.environ.get("LF_REPORT_PDF_BACKEND", "chromium").lower() == "wkhtmltopdf":
            path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
            self._write_pdf_file(self.write_output_html, self.write_output_pdf, options, configuration=config)
        else:
            self._write_pdf_file(self.write_output_html, self.write_output_pdf, options)

    _ASSET_MIME_TYPES = {".css": "text/css", ".js": "text/javascript", ".png": "image/png", ".woff": "font/woff"}

    def _read_report_asset(self, filename):
        """Reads a file already copied into this report's folder. Returns "" if it's missing,
        so a report still builds (just without that one piece) instead of crashing.

        Args:
            filename (str): asset file name, relative to the report folder.

        Returns:
            str: the file's contents, or "" if it's missing.

        Example:
            css_text = report._read_report_asset("report.css")
        """
        try:
            with open(os.path.join(self.path_date_time, filename), "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            return ""

    def _report_asset_as_data_uri(self, filename):
        """Turns a report asset (an image, a font) into a "data:...;base64,..." string that can go
        straight into an src="..." attribute, so the browser doesn't need to fetch a separate file.

        Args:
            filename (str): asset file name, relative to the report folder.

        Returns:
            str: the data URI, or the plain filename if the file is missing.

        Example:
            logo_uri = report._report_asset_as_data_uri("yellow.png")
        """
        try:
            with open(os.path.join(self.path_date_time, filename), "rb") as f:
                raw_bytes = f.read()
        except OSError:
            return filename
        ext = os.path.splitext(filename)[1].lower()
        mime = self._ASSET_MIME_TYPES.get(ext, "application/octet-stream")
        return "data:{};base64,{}".format(mime, base64.b64encode(raw_bytes).decode("ascii"))

    def _load_report_js(self):
        """Reads report_v2.js from the artifacts folder and fills in the chart palette.

        Returns:
            str: the JavaScript for charts, tables, sorting and search.

        Example:
            report_js = report._load_report_js()
        """
        path = os.path.join(self.current_path, self.banner_directory, "report_v2.js")
        with open(path, "r", encoding="utf-8") as f:
            return f.read().replace("__LF_PALETTE__", json.dumps(self._echarts_palette))

    def get_html_head(self, title='Untitled'):
        """Returns the HTML <head> with the CSS, font and chart script inlined,
        so the single .html file works without its folder.

        Args:
            title (str): page title.

        Returns:
            str: the <head>...</head> markup.

        Example:
            head_html = report.get_html_head(title="My Test Report")
        """
        report_css = self._read_report_asset("report.css")
        font_data_uri = self._report_asset_as_data_uri(self.font_file)
        report_css = report_css.replace('url("{}")'.format(self.font_file), 'url("{}")'.format(font_data_uri))
        custom_css = self._read_report_asset("custom.css")
        echarts_js = self._read_report_asset(self.echarts_file)
        report_js = self._load_report_js()
        return """<head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1' />
        <style>
        body {{ margin: 0; padding: 0; }}
        </style>
        <style>
        {report_css}
        </style>
        <style>
        {custom_css}
        </style>
        <script>
        {echarts_js}
        </script>
        <script>
        {report_js}
        </script>
        <title>{title}</title>
    </head>""".format(title=title, report_css=report_css, custom_css=custom_css, echarts_js=echarts_js,
                      report_js=report_js)

    def build_banner(self):
        """Starts the page and adds the top banner with the title, date and logo on the right.

        Example:
            report.build_banner()
        """
        self.banner_html = """<!DOCTYPE html>
<html lang='en'>
    {head_tag}
    <body>
        <div class='report-shell'>
        <div id='BannerBack'>
            <div id='Banner'>
                <div class='HeaderStyle'>
                    <h1 class='TitleFontPrint'>{title}</h1>
                    <h4 class='TitleFontPrintSub'>{date}</h4>
                </div>
                <img id='BannerLogo' align='left' src="{logo_data_uri}" border='0'/>
            </div>
        </div>
                 """.format(
            head_tag=self.get_html_head(title=self.title),
            logo_data_uri=self._report_asset_as_data_uri(self.logo_file_name),
            title=self.title,
            date=self.date,
        )
        self.html += self.banner_html

    def build_table_title(self):
        """Adds the table heading set by set_table_title().

        Example:
            report.set_table_title("Station Results")
            report.build_table_title()
        """
        self.table_title_html = """
                    <!-- Table Title-->
                    <h3 align='left'>{title}</h3>
                    """.format(title=self.table_title)
        self.html += self.table_title_html

    def start_content_div(self):
        """Opens a 'contentDiv' section; close it with end_content_div().

        Example:
            report.start_content_div()
        """
        self.html += "\n<div class='contentDiv'>\n"

    @staticmethod
    def _keep_identifiers_on_one_line(table_html, dataframe):
        """Mark SSID, BSSID, and MAC cells so print CSS keeps their values intact.

        Args:
            table_html (str): HTML produced by DataFrame.to_html() for the table.
            dataframe (DataFrame): the table the HTML was generated from, used to find
                which columns are SSID/BSSID/MAC identifier columns.

        Returns:
            str: the table HTML with identifier cells tagged with class="network-identifier".

        Example:
            html = lf_report._keep_identifiers_on_one_line(table_html, dataframe)
        """
        identifier_columns = {
            index for index, name in enumerate(dataframe.columns)
            if re.search(r'\b(?:ssid|bssid|mac)\b', str(name), re.IGNORECASE)
        }
        if not identifier_columns:
            return table_html

        def mark_row(match):
            cell_index = -1

            def mark_cell(cell):
                nonlocal cell_index
                cell_index += 1
                if cell_index in identifier_columns:
                    return cell.group(0)[:-1] + ' class="network-identifier">'
                return cell.group(0)

            return re.sub(r'<td\b[^>]*>', mark_cell, match.group(0))

        return re.sub(r'<tr\b[^>]*>.*?</tr>', mark_row, table_html, flags=re.DOTALL)

    def build_table(self):
        """Adds the current table (set by set_table_dataframe) to the report.

        Example:
            report.set_table_dataframe(dataframe)
            report.build_table()
        """
        self.dataframe_html = self.dataframe.to_html(index=False, justify='center', classes='data-table')
        self.dataframe_html = self._keep_identifiers_on_one_line(self.dataframe_html, self.dataframe)
        self.html += "<div class='table-wrap'>" + self.dataframe_html + "</div>"

    def rating_build_table(self, rating_column, rating_colors):
        """Like pass_failed_build_table(), but for any column of rating labels (e.g.
        "Excellent"/"Good"/"Average"/"Poor") instead of a fixed Success/Failed pair.

        Args:
            rating_column (str): name of the column to show as colored badges.
            rating_colors (dict): maps each label to a CSS color; labels missing from it
                stay plain text.

        Example:
            report.set_table_dataframe(dataframe)
            report.rating_build_table("Rating", {"Excellent": "#1e7e34", "Poor": "#e74c3c"})
        """
        def _badge(value):
            """Wraps a known rating label in a colored badge; other values are left as they are.

            Args:
                value: the cell value.

            Returns:
                str: badge HTML if value is a known rating label, or value unchanged otherwise.
            """
            color = rating_colors.get(value)
            if not color:
                return value
            return ("<span style='background:{color}; color:#fff; padding:2px 10px; "
                    "border-radius:10px; font-weight:600; white-space:nowrap;'>{value}</span>"
                    ).format(color=color, value=value)

        badge_df = self.dataframe.copy()
        badge_df[rating_column] = badge_df[rating_column].apply(_badge)
        self.dataframe_html = badge_df.to_html(index=False, justify='center', classes='data-table', escape=False)
        self.dataframe_html = self._keep_identifiers_on_one_line(self.dataframe_html, badge_df)
        self.html += "<div class='table-wrap'>" + self.dataframe_html + "</div>"

    def build_footer(self):
        """Adds the footer with the Candela logo and closes the page layout.

        Example:
            report.build_footer()
        """
        self.footer_html = """
    <footer class='FooterStyle'>
        <a href="https://www.candelatech.com/"><img
            id='BannerLogoFooter' align='right' src="{logo_footer_data_uri}" border='0'/></a>
        <p>Generated by Candela Technologies LANforge network testing tool</p>
        <p><a href="https://www.candelatech.com">www.candelatech.com</a><p>
    </footer>
    </div><!-- end report-shell -->
        """.format(logo_footer_data_uri=self._report_asset_as_data_uri(self.logo_footer_file_name))
        self.html += self.footer_html

    def build_custom(self):
        """Adds the raw HTML set by set_custom_html().

        Example:
            report.set_custom_html("<p>Custom section</p>")
            report.build_custom()
        """
        self.html += self.custom_html

    def build_objective(self):
        """Adds a heading and paragraph section, using the text from set_obj_html().

        Example:
            report.set_obj_html("Objective", "Verify throughput under load.")
            report.build_objective()
        """
        self.obj_html = """
            <!-- Test Objective -->
            <div class='chart-card' style='text-align:left;'>
              <h3 align='left'>{title}</h3>
              <p align='left' width='900'>{objective}</p>
            </div>
            """.format(title=self.obj_title,
                       objective=self.objective)
        self.html += self.obj_html

    def build_graph(self):
        """Adds the graph set by set_graph_image(): a PNG inside a chart card,
        or an interactive chart as it is.

        Example:
            report.set_graph_image("throughput.png")
            report.build_graph()
        """
        content = str(self.graph_image)
        if self._chart_markup_sentinel in content:
            # Interactive chart markup: add it as is, not inside an <img> tag.
            self.graph_html_obj = content
        else:
            self.graph_html_obj = """
            <div class='chart-card'>
              <img src='{image}' alt='' />
            </div>
            """.format(image=content)
        self.html += self.graph_html_obj

    def end_content_div(self):
        """Closes a section opened with start_content_div() or start_content_div2().

        Example:
            report.end_content_div()
        """
        self.html += "\n</div><!-- end contentDiv -->\n"

    def build_chart_title(self, chart_title):
        """Adds a chart heading.

        Args:
            chart_title (str): heading text.

        Example:
            report.build_chart_title("Throughput Over Time")
        """
        self.chart_title_html = """
            <div class='HeaderStyle'>
                <h3 class='TitleFontPrint'>{title}</h3>
            """.format(title=chart_title)
        self.html += self.chart_title_html

    def build_info_card(self, title, items, icon=None, card_id=None):
        """Adds a titled card showing a grid of icon + label + value blocks, e.g. a test's
        configuration summary.

        Args:
            title (str): card header text.
            items (list): [{"icon": ..., "label": ..., "value": ...}, ...]; items with no value are skipped.
            icon: icon shown next to the card's own title, not the individual items.
            card_id (str): optional DOM id for the card.

        Example:
            report.build_info_card("Test Configuration", [
                {"icon": "&#9881;", "label": "SSID", "value": "my-ssid"},
                {"icon": "&#128225;", "label": "Band", "value": "5 GHz"},
            ])
        """
        rows = []
        for item in items or []:
            value = item.get("value")
            # Treat the text "None" (from str(None)) as empty.
            if value is None or str(value).strip() == "" or str(value).strip().lower() == "none":
                continue
            item_icon_html = "<div class='icon-badge'>{}</div>".format(item["icon"]) if item.get("icon") else ""
            rows.append("""
                <div class='info-item'>
                  {icon}
                  <div class='info-item-body'>
                    <div class='info-item-label'>{label}</div>
                    <div class='info-item-value'>{value}</div>
                  </div>
                </div>
                """.format(icon=item_icon_html, label=item.get("label", ""), value=value))

        id_attr = " id='{}'".format(card_id) if card_id else ""
        header_icon_html = "<div class='icon-badge'>{}</div>".format(icon) if icon else ""

        self.html += """
                <div class='info-card'{id_attr}>
                  <div class='info-card-header'>{header_icon}{title}</div>
                  <div class='info-grid'>{rows}</div>
                </div>
                """.format(id_attr=id_attr, header_icon=header_icon_html, title=title, rows="".join(rows))

    def build_findings_card(self, title, findings, card_id=None):
        """Adds a "Key Findings" card: a short bulleted list of plain-English observations,
        each tagged with a severity marker (checkmark/dot/warning/cross).

        Args:
            title (str): card header text.
            findings (list): [{"type": "positive"|"neutral"|"warning"|"critical", "text": ...}, ...],
                most important first.
            card_id (str): optional DOM id for the card.

        Example:
            report.build_findings_card("Key Findings", [
                {"type": "positive", "text": "Throughput met the target on all stations."},
                {"type": "warning", "text": "One station dropped connectivity briefly."},
            ])
        """
        items = []
        for f in findings or []:
            text = f.get("text")
            if not text or not str(text).strip():
                continue
            ftype = f.get("type") if f.get("type") in self._finding_type_icon else "neutral"
            items.append("""
                <li class='finding finding-{ftype}'>
                  <span class='finding-icon'>{icon}</span>
                  <span class='finding-text'>{text}</span>
                </li>
                """.format(ftype=ftype, icon=self._finding_type_icon[ftype], text=text))

        id_attr = " id='{}'".format(card_id) if card_id else ""

        if not items:
            self.html += """
                <div class='info-card'{id_attr}>
                  <div class='info-card-header'>{title}</div>
                  <p style='color:var(--muted);'>No findings available for this data.</p>
                </div>
                """.format(id_attr=id_attr, title=title)
            return

        self.html += """
                <div class='info-card'{id_attr}>
                  <div class='info-card-header'>{title}</div>
                  <ul class='findings-list'>{items}</ul>
                </div>
                """.format(id_attr=id_attr, title=title, items="".join(items))

    def build_device_summary_card(self, devices, name_field="name", platform_field="platform",
                                  columns=None, platform_icons=None, page_size=10,
                                  card_id=None, title="Devices"):
        """Adds a device summary card: total/per-category counts, a donut breakdown, and a
        searchable, paginated table. Also handles the one-time ECharts + search-table
        runtime injection.

        Args:
            devices (list): dicts, e.g. [{"name": "vivo V12", "platform": "Android"}, ...].
            name_field (str): key in each device dict holding its display name.
            platform_field (str): key in each device dict holding its category, used for the counts/donut.
            columns (list): table columns, e.g. [{"key": ..., "label": ...}, ...]; defaults to name + platform.
            platform_icons (dict): {category_value: icon} shown next to that category's count.
            page_size (int): initial rows-per-page for the table.
            card_id (str): id prefix for the card; auto-generated if left blank.
            title (str): card header text.

        Example:
            report.build_device_summary_card([
                {"name": "vivo V12", "platform": "Android"},
                {"name": "iPhone 13", "platform": "iOS"},
            ])
        """
        devices = devices or []
        if not card_id:
            self._chart_id_counter += 1
            card_id = "device-summary-{}".format(self._chart_id_counter)
        columns = columns or [{"key": name_field, "label": "Device Name"}, {"key": platform_field, "label": "OS type"}]
        platform_icons = platform_icons or {}

        if not devices:
            self.html += """
                <div class='info-card' id='{card_id}'>
                  <div class='info-card-header'>{title}</div>
                  <p style='color:var(--muted);'>No devices to show.</p>
                </div>
                """.format(card_id=card_id, title=title)
            return

        total = len(devices)
        platform_counts = {}
        for d in devices:
            p = d.get(platform_field) or "Unknown"
            platform_counts[p] = platform_counts.get(p, 0) + 1
        # Count-descending so the biggest group leads, same as the stat row.
        ordered_platforms = sorted(platform_counts, key=lambda p: -platform_counts[p])

        stat_items = "".join("""
                <div class='device-stat'>
                  <div class='icon-badge'>{icon}</div>
                  <div>
                    <div class='stat-value'>{count}</div>
                    <div class='stat-label'>{label}</div>
                  </div>
                </div>
                """.format(icon=platform_icons.get(p, self._platform_icons.get(str(p).strip().lower(), "&bull;")), count=platform_counts[p], label=p)
            for p in ordered_platforms)
        stats_html = """
                <div class='device-stats-col'>
                  <div class='device-stat'>
                    <div class='icon-badge'>&#9679;</div>
                    <div>
                      <div class='stat-value'>{total}</div>
                      <div class='stat-label'>Total Devices</div>
                    </div>
                  </div>
                  {stat_items}
                </div>
                """.format(total=total, stat_items=stat_items)

        legend_items = []
        for i, p in enumerate(ordered_platforms):
            count = platform_counts[p]
            pct = count / total * 100
            color = self._echarts_palette[i % len(self._echarts_palette)]
            legend_items.append("""
                <div class='device-legend-item'>
                  <span class='device-legend-dot' style='background:{color}'></span>
                  <span class='device-legend-name'>{name} ({count})</span>
                  <span class='device-legend-pct'>{pct:.1f}%</span>
                </div>
                """.format(color=color, name=p, count=count, pct=pct))

        # Reuse lf_pie_graph for the donut data only; this card draws its own title and legend.
        donut_pie = lf_pie_graph(
            _data_set=[platform_counts[p] for p in ordered_platforms],
            _label=ordered_platforms,
            _legend=False,
            _show_labels=False,
            _tooltip_formatter="{b}: {c} ({d}%)",
        )
        donut_id, donut_payload = donut_pie.build_pie_payload(chart_id="{}-donut".format(card_id))
        donut_html = """
                <div class='device-donut-col'>
                  <div id='{donut_id}' class='device-donut'></div>
                  <div class='device-legend'>{legend}</div>
                </div>
                <script>
                  window.__lfModernReport.renderPieChart({donut_id_json}, {donut_payload});
                </script>
                """.format(donut_id=donut_id, legend="".join(legend_items),
                           donut_id_json=json.dumps(donut_id), donut_payload=json.dumps(donut_payload))

        rows_payload = []
        for d in devices:
            cells = "".join("<td>{}</td>".format(d.get(c["key"], "")) for c in columns)
            rows_payload.append({"cellsHtml": cells})
        header_cells = "".join("<th>{}</th>".format(c["label"]) for c in columns)

        default_page_size = min(page_size, total) if page_size else total
        size_choices = sorted({n for n in (5, 10, 25, 50, default_page_size) if n <= total})
        page_size_options = "".join(
            "<option value='{n}'{sel}>{n}</option>".format(n=n, sel=" selected" if n == default_page_size else "")
            for n in size_choices
        ) + "<option value='all'>All</option>"

        self.html += """
                <div class='info-card' id='{card_id}'>
                  <div class='info-card-header'>{title}</div>
                  <div class='device-summary-row'>
                    {stats}
                    {donut}
                  </div>
                  <div class='device-toolbar'>
                    <button class='btn-outline view-all-btn' type='button'>View All Devices</button>
                  </div>
                  <p class='device-count-label'></p>
                  <div class='table-wrap'>
                    <table class='device-table'>
                      <thead><tr><th>S.No.</th>{header_cells}</tr></thead>
                      <tbody></tbody>
                    </table>
                  </div>
                  <div class='device-footer'>
                    <div class='rows-per-page'>Rows per page: <select>{page_size_options}</select></div>
                    <div class='pagination'></div>
                  </div>
                  <script>
                    window.__lfModernReport.initSearchTable({card_id_json}, {rows}, {default_page_size});
                  </script>
                </div>
                """.format(
            card_id=card_id, title=title, stats=stats_html, donut=donut_html,
            header_cells=header_cells, page_size_options=page_size_options,
            card_id_json=json.dumps(card_id), rows=json.dumps(rows_payload),
            default_page_size=default_page_size,
        )


if __name__ == "__main__" and _IS_PDF_WORKER:
    _run_pdf_worker()
    sys.exit(0)

# Unit Test
if __name__ == "__main__":
    help_summary = '''\
     Builds LANforge test reports (HTML and PDF) with graphs, tables and an objective/description
     section. Modern-report-styled drop-in replacement for lf_report.py -- same API, new look.
    '''
    parser = argparse.ArgumentParser(
        prog="lf_report_v2.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Modern reporting library Unit Test")
    parser.add_argument('--lfmgr', help='sample argument: where LANforge GUI is running', default='localhost')
    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")
    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    logger.info("LANforge manager {lfmgr}".format(lfmgr=args.lfmgr))

    dataframe = pd.DataFrame({
        'product': ['CT521a-264-1ac-1n', 'CT521a-1ac-1ax', 'CT522-264-1ac2-1n', 'CT523c-2ac2-db-10g-cu',
                    'CT523c-3ac2-db-10g-cu', 'CT523c-8ax-ac10g-cu', 'CT523c-192-2ac2-1ac-10g'],
        'radios': [1, 1, 2, 2, 6, 9, 3],
        'MIMO': ['N', 'N', 'N', 'Y', 'Y', 'Y', 'Y'],
        'stations': [200, 64, 200, 128, 384, 72, 192],
        'mbps': [300, 300, 300, 10000, 10000, 10000, 10000]
    })

    logger.info(dataframe)

    dataframe2 = pd.DataFrame({
        'station': [1, 2, 3, 4, 5, 6, 7],
        'time_seconds': [23, 78, 22, 19, 45, 22, 25]
    })

    report = lf_report()
    report.set_title("Banner Title One")
    report.build_banner()

    report.set_table_title("Title One")
    report.build_table_title()

    report.set_table_dataframe(dataframe)
    report.build_table()

    report.set_table_title("Title Two")
    report.build_table_title()

    report.set_table_dataframe(dataframe2)
    report.build_table()

    # lf_pie_graph demo.
    pie = lf_pie_graph(_data_set=[40, 45, 15],
                       _label=["2.4 GHz", "5 GHz", "6 GHz"],
                       _graph_title="Band Distribution",
                       _graph_image_name="demo-band-distribution")
    report.set_graph_image(pie.build_pie_graph())
    report.build_graph()

    report.build_footer()

    html_file = report.write_html()
    logger.info("returned file ")
    logger.info(html_file)
    report.write_pdf()

    logger.info("report path {}".format(report.path))
