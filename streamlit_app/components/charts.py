"""
Plotly Chart Generators for NovaNest Analytics Platform
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.settings import PLOTLY_TEMPLATE

def plot_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, labels: dict = None):
    """Renders a clean Plotly line chart."""
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title,
        labels=labels,
        template=PLOTLY_TEMPLATE,
        markers=True
    )
    fig.update_layout(xaxis_title="", yaxis_title="", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, orientation: str = "v", color_col: str = None):
    """Renders a responsive Plotly bar chart."""
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        orientation=orientation,
        color=color_col if color_col else y_col if orientation == "v" else x_col,
        template=PLOTLY_TEMPLATE,
        color_continuous_scale="Viridis"
    )
    fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_donut_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str):
    """Renders a Plotly donut chart."""
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        title=title,
        hole=0.4,
        template=PLOTLY_TEMPLATE
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_funnel_chart(df: pd.DataFrame, stage_col: str, value_col: str, title: str):
    """Renders a Plotly clickstream conversion funnel chart."""
    fig = go.Figure(go.Funnel(
        y=df[stage_col],
        x=df[value_col],
        textinfo="value+percent initial",
        marker=dict(color=["#1E88E5", "#00BCD4", "#009688", "#4CAF50", "#8BC34A", "#CDDC39"])
    ))
    fig.update_layout(title=title, template=PLOTLY_TEMPLATE, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_histogram(df: pd.DataFrame, x_col: str, title: str, nbins: int = 30):
    """Renders a distribution histogram."""
    fig = px.histogram(
        df,
        x=x_col,
        title=title,
        nbins=nbins,
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#FF4B4B"]
    )
    fig.update_layout(xaxis_title="", yaxis_title="Count", margin=dict(l=20, r=20, t=40, b=20))
    return fig
