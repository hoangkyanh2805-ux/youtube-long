#!/usr/bin/env python3
"""Dashboard UI — lấy từ DarioPTWR/Youtube-Analytics-Dashboard.

Features:
- Chart patterns (pie, scatter, bar, box, histogram)
- Layout patterns (sidebar, columns, tabs)
- Styling (dark mode, custom CSS)
- Data visualization helpers

Usage:
    from dashboard_ui import DashboardUI
    ui = DashboardUI()
    html = ui.create_pie_chart(data, "Channel Popularity")
    html = ui.create_bar_chart(data, "Top 10 Videos")
    html = ui.create_scatter_plot(data, "Views vs Duration")
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)


class DashboardUI:
    """Dashboard UI helpers — Streamlit patterns → HTML/JS."""

    def __init__(self, theme: Literal["dark", "light"] = "dark"):
        self.theme = theme
        self.colors = {
            "dark": {
                "bg": "#0f1216",
                "sf": "#171c22",
                "sf2": "#1e242c",
                "bd": "#2c343d",
                "tx": "#e6edf5",
                "mu": "#94a3b8",
                "bl": "#60a5fa",
                "gr": "#4ade80",
                "am": "#fbbf24",
                "rd": "#f87171",
                "ac": "#38bdf8",
            },
            "light": {
                "bg": "#ffffff",
                "sf": "#f8fafc",
                "sf2": "#f1f5f9",
                "bd": "#e2e8f0",
                "tx": "#1e293b",
                "mu": "#64748b",
                "bl": "#3b82f6",
                "gr": "#22c55e",
                "am": "#f59e0b",
                "rd": "#ef4444",
                "ac": "#0ea5e9",
            },
        }

    # ── Layout Patterns ───────────────────────────────────────────────────

    def create_sidebar(self, title: str, description: str = "") -> str:
        """Create sidebar HTML."""
        c = self.colors[self.theme]
        return f"""
<div class="sidebar" style="background-color: {c['sf']}; color: {c['tx']}; padding: 20px; border-radius: 10px;">
    <h2 style="color: {c['bl']}; margin-top: 0;">{title}</h2>
    <p style="color: {c['mu']};">{description}</p>
</div>
"""

    def create_columns(self, n: int, *contents: str) -> str:
        """Create column layout."""
        cols = "".join(f'<div class="col">{c}</div>' for c in contents)
        return f'<div class="columns" style="display: grid; grid-template-columns: repeat({n}, 1fr); gap: 20px;">{cols}</div>'

    def create_tabs(self, tabs: list[tuple[str, str]]) -> str:
        """Create tab layout.

        Input: [("Tab1", "content1"), ("Tab2", "content2"), ...]
        """
        tab_btns = "".join(
            f'<button class="tab-btn" data-tab="{t[0]}" onclick="switchTab(\'{t[0]}\')">{t[0]}</button>'
            for t in tabs
        )
        tab_panels = "".join(
            f'<div class="tab-panel" id="tab-{t[0]}">{t[1]}</div>'
            for t in tabs
        )
        return f"""
<div class="tabs">
    {tab_btns}
    {tab_panels}
</div>
"""

    def create_metric_card(self, label: str, value: str, note: str = "") -> str:
        """Create metric card."""
        c = self.colors[self.theme]
        return f"""
<div class="metric-card" style="background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; padding: 15px;">
    <div style="color: {c['mu']}; font-size: 12px; text-transform: uppercase;">{label}</div>
    <div style="color: {c['tx']}; font-size: 24px; font-weight: bold;">{value}</div>
    <div style="color: {c['mu']}; font-size: 11px;">{note}</div>
</div>
"""

    def create_data_table(self, headers: list[str], rows: list[list]) -> str:
        """Create data table."""
        c = self.colors[self.theme]
        header_html = "".join(f"<th>{h}</th>" for h in headers)
        rows_html = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in rows
        )
        return f"""
<table style="width: 100%; border-collapse: collapse; background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; overflow: hidden;">
    <thead>
        <tr style="background-color: {c['sf2']};">
            {header_html}
        </tr>
    </thead>
    <tbody>
        {rows_html}
    </tbody>
</table>
"""

    # ── Chart Patterns (Plotly → HTML/JS) ─────────────────────────────────

    def create_pie_chart(self, data: list[dict], title: str, value_key: str = "value", label_key: str = "label") -> str:
        """Create pie chart (Plotly-style).

        Input: [{"label": "A", "value": 10}, ...]
        """
        c = self.colors[self.theme]
        labels = [d[label_key] for d in data]
        values = [d[value_key] for d in data]
        colors = px_colors(len(data))

        return f"""
<div class="chart-container" style="background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; padding: 15px;">
    <h3 style="color: {c['tx']}; margin-top: 0;">{title}</h3>
    <div id="pie-chart"></div>
    <script>
        var data = [{{
            values: {json.dumps(values)},
            labels: {json.dumps(labels)},
            type: 'pie',
            hole: 0.4,
            marker: {{ colors: {json.dumps(colors)} }},
            textposition: 'inside',
            textinfo: 'percent+label'
        }}];
        var layout = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '{c['tx']}' }},
            showlegend: false
        }};
        Plotly.newPlot('pie-chart', data, layout, {{responsive: true}});
    </script>
</div>
"""

    def create_bar_chart(self, data: list[dict], title: str, x_key: str = "x", y_key: str = "y") -> str:
        """Create bar chart.

        Input: [{"x": "A", "y": 10}, ...]
        """
        c = self.colors[self.theme]
        x = [d[x_key] for d in data]
        y = [d[y_key] for d in data]

        return f"""
<div class="chart-container" style="background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; padding: 15px;">
    <h3 style="color: {c['tx']}; margin-top: 0;">{title}</h3>
    <div id="bar-chart"></div>
    <script>
        var data = [{{
            x: {json.dumps(x)},
            y: {json.dumps(y)},
            type: 'bar',
            marker: {{ color: '{c['bl']}' }}
        }}];
        var layout = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '{c['tx']}' }},
            xaxis: {{ title: '{x_key}' }},
            yaxis: {{ title: '{y_key}' }}
        }};
        Plotly.newPlot('bar-chart', data, layout, {{responsive: true}});
    </script>
</div>
"""

    def create_scatter_plot(self, data: list[dict], title: str, x_key: str = "x", y_key: str = "y") -> str:
        """Create scatter plot.

        Input: [{"x": 10, "y": 20}, ...]
        """
        c = self.colors[self.theme]
        x = [d[x_key] for d in data]
        y = [d[y_key] for d in data]

        return f"""
<div class="chart-container" style="background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; padding: 15px;">
    <h3 style="color: {c['tx']}; margin-top: 0;">{title}</h3>
    <div id="scatter-plot"></div>
    <script>
        var data = [{{
            x: {json.dumps(x)},
            y: {json.dumps(y)},
            mode: 'markers',
            type: 'scatter',
            marker: {{ color: '{c['gr']}', size: 10 }}
        }}];
        var layout = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '{c['tx']}' }},
            xaxis: {{ title: '{x_key}' }},
            yaxis: {{ title: '{y_key}' }}
        }};
        Plotly.newPlot('scatter-plot', data, layout, {{responsive: true}});
    </script>
</div>
"""

    def create_histogram(self, data: list[float], title: str, nbins: int = 50) -> str:
        """Create histogram.

        Input: [10, 20, 30, ...]
        """
        c = self.colors[self.theme]

        return f"""
<div class="chart-container" style="background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; padding: 15px;">
    <h3 style="color: {c['tx']}; margin-top: 0;">{title}</h3>
    <div id="histogram"></div>
    <script>
        var data = [{{
            x: {json.dumps(data)},
            type: 'histogram',
            nbinsx: {nbins},
            marker: {{ color: '{c['am']}' }}
        }}];
        var layout = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '{c['tx']}' }},
            xaxis: {{ title: 'Value' }},
            yaxis: {{ title: 'Count' }}
        }};
        Plotly.newPlot('histogram', data, layout, {{responsive: true}});
    </script>
</div>
"""

    def create_box_plot(self, data: list[dict], title: str, x_key: str = "x", y_key: str = "y") -> str:
        """Create box plot.

        Input: [{"x": "A", "y": 10}, ...]
        """
        c = self.colors[self.theme]
        x = [d[x_key] for d in data]
        y = [d[y_key] for d in data]

        return f"""
<div class="chart-container" style="background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; padding: 15px;">
    <h3 style="color: {c['tx']}; margin-top: 0;">{title}</h3>
    <div id="box-plot"></div>
    <script>
        var data = [{{
            x: {json.dumps(x)},
            y: {json.dumps(y)},
            type: 'box',
            marker: {{ color: '{c['ac']}' }}
        }}];
        var layout = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '{c['tx']}' }},
            xaxis: {{ title: '{x_key}' }},
            yaxis: {{ title: '{y_key}' }}
        }};
        Plotly.newPlot('box-plot', data, layout, {{responsive: true}});
    </script>
</div>
"""

    # ── Styling ───────────────────────────────────────────────────────────

    def get_css(self) -> str:
        """Get custom CSS."""
        c = self.colors[self.theme]
        return f"""
<style>
    .sidebar {{ background-color: {c['sf']}; color: {c['tx']}; padding: 20px; border-radius: 10px; }}
    .sidebar h2 {{ color: {c['bl']}; margin-top: 0; }}
    .sidebar p {{ color: {c['mu']}; }}
    .metric-card {{ background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; padding: 15px; }}
    .chart-container {{ background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; padding: 15px; }}
    .tab-btn {{ background-color: {c['sf']}; border: 1px solid {c['bd']}; color: {c['mu']}; padding: 8px 16px; border-radius: 8px; cursor: pointer; }}
    .tab-btn:hover {{ background-color: {c['sf2']}; color: {c['tx']}; }}
    .tab-btn.active {{ background-color: {c['bl']}; color: #fff; border-color: {c['bl']}; }}
    .tab-panel {{ display: none; padding-top: 20px; }}
    .tab-panel.active {{ display: block; }}
    table {{ width: 100%; border-collapse: collapse; background-color: {c['sf']}; border: 1px solid {c['bd']}; border-radius: 10px; overflow: hidden; }}
    th {{ background-color: {c['sf2']}; color: {c['mu']}; padding: 10px; text-align: left; }}
    td {{ padding: 8px 10px; border-bottom: 1px solid {c['bd']}; color: {c['tx']}; }}
    tr:last-child td {{ border-bottom: none; }}
</style>
"""


def px_colors(n: int) -> list[str]:
    """Generate Plotly-style colors."""
    base_colors = [
        "#636efa", "#ef553b", "#00cc96", "#ab63fa", "#ffa15a",
        "#19d3f3", "#ff6692", "#b6e880", "#ff97ff", "#fecb52",
    ]
    return [base_colors[i % len(base_colors)] for i in range(n)]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ui = DashboardUI(theme="dark")

    # Test layouts
    print("Testing DashboardUI...")
    print()

    # Sidebar
    sidebar = ui.create_sidebar("YouTube Analytics", "Track key metrics and trends")
    print(f"Sidebar: {len(sidebar)} chars")

    # Metric card
    card = ui.create_metric_card("Views", "9,016", "28 days")
    print(f"Metric card: {len(card)} chars")

    # Data table
    table = ui.create_data_table(
        ["Channel", "Views", "Videos"],
        [["Azzam", "9,016", "297"], ["GoldTrader", "1,406,625", "742"]]
    )
    print(f"Data table: {len(table)} chars")

    # Charts
    pie = ui.create_pie_chart(
        [{"label": "A", "value": 10}, {"label": "B", "value": 20}],
        "Channel Popularity"
    )
    print(f"Pie chart: {len(pie)} chars")

    bar = ui.create_bar_chart(
        [{"x": "A", "y": 10}, {"x": "B", "y": 20}],
        "Top Videos"
    )
    print(f"Bar chart: {len(bar)} chars")

    scatter = ui.create_scatter_plot(
        [{"x": 10, "y": 20}, {"x": 20, "y": 30}],
        "Views vs Duration"
    )
    print(f"Scatter plot: {len(scatter)} chars")

    hist = ui.create_histogram([10, 20, 30, 40, 50], "View Distribution")
    print(f"Histogram: {len(hist)} chars")

    box = ui.create_box_plot(
        [{"x": "A", "y": 10}, {"x": "B", "y": 20}],
        "Views by Duration"
    )
    print(f"Box plot: {len(box)} chars")

    print()
    print("All UI components loaded successfully!")
