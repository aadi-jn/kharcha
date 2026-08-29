"""Altair chart helpers. Each encodes the app_plan.md design rules once:

- form picked from the data's job, colour last
- categorical colour from the fixed map in theme.py (follows the entity, not rank)
- one axis, never two
- tooltips always on; the caller pairs every chart with a table view
- chrome (axes, grid, background) comes from Streamlit's chart theme, light or dark
"""

from __future__ import annotations

import altair as alt
import pandas as pd

from lib.theme import (
    CATEGORY_COLOURS,
    INSTRUMENT_COLOURS,
    SEQUENTIAL_HUE,
)


def _rupees(col: str) -> alt.Tooltip:
    return alt.Tooltip(col, format=",.0f", title="₹")


def monthly_trend_chart(df: pd.DataFrame) -> alt.Chart:
    """Stacked column: net spend by month, coloured by category (top-7 + Other)."""
    present = [c for c in CATEGORY_COLOURS if c in set(df["category"])]
    return (
        alt.Chart(df)
        .mark_bar(stroke="white", strokeWidth=1)
        .encode(
            x=alt.X("txn_month:O", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("net_spend:Q", title="Net spend (₹)", stack="zero"),
            color=alt.Color(
                "category:N",
                title="Category",
                scale=alt.Scale(
                    domain=present,
                    range=[CATEGORY_COLOURS[c] for c in present],
                ),
                sort=present,
            ),
            order=alt.Order("net_spend:Q", sort="descending"),
            tooltip=["txn_month", "category", _rupees("net_spend")],
        )
        .properties(height=340)
    )


def ranked_bar_chart(
    df: pd.DataFrame, category_field: str, value_field: str, title: str
) -> alt.Chart:
    """Single-hue horizontal bars for a magnitude ranking."""
    return (
        alt.Chart(df)
        .mark_bar(color=SEQUENTIAL_HUE, cornerRadiusEnd=4)
        .encode(
            x=alt.X(f"{value_field}:Q", title=title),
            y=alt.Y(f"{category_field}:N", title=None, sort="-x"),
            tooltip=[category_field, _rupees(value_field)],
        )
        .properties(height=40 * len(df) + 20)
    )


def payment_mix_chart(df: pd.DataFrame) -> alt.Chart:
    """One horizontal bar, segmented by payment instrument."""
    present = [i for i in INSTRUMENT_COLOURS if i in set(df["instrument"])]
    return (
        alt.Chart(df.assign(_all="Recorded spend"))
        .mark_bar(stroke="white", strokeWidth=1)
        .encode(
            x=alt.X("spend:Q", title="Recorded spend (₹)", stack="zero"),
            y=alt.Y("_all:N", title=None),
            color=alt.Color(
                "instrument:N",
                title="Instrument",
                scale=alt.Scale(
                    domain=present, range=[INSTRUMENT_COLOURS[i] for i in present]
                ),
                sort=present,
            ),
            order=alt.Order("spend:Q", sort="descending"),
            tooltip=["instrument", _rupees("spend"), "txn_count"],
        )
        .properties(height=120)
    )
