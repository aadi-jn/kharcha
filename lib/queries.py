"""One function per Overview view. Each returns a tidy DataFrame; the page layer
does the formatting and charting. All queries hit the Layer 2 views (project + dataset from secrets).
"""

from __future__ import annotations

import pandas as pd

from lib.bq import run_query, table
from lib.theme import CATEGORY_GROUP_ORDER, INSTRUMENT_LABELS, fold_to_top7

TXNS = table("transactions")
MONTHLY = table("monthly_category_spend")


def headline_kpis() -> dict:
    """Net spend, common-window avg/month, cost of credit, top category, counts."""
    df = run_query(f"""
        SELECT
          SUM(net_amount)                                              AS net_spend,
          SUM(IF(category_group = 'Cost of credit', net_amount, 0))    AS cost_of_credit,
          SUM(IF(in_common_window, net_amount, 0))                     AS net_spend_common,
          COUNT(DISTINCT IF(in_common_window, txn_month, NULL))        AS common_months,
          COUNT(*)                                                     AS txn_count,
          MIN(txn_date)                                                AS first_date,
          MAX(txn_date)                                                AS last_date
        FROM {TXNS}
    """).iloc[0]

    top = run_query(f"""
        SELECT category, SUM(net_spend) AS net
        FROM {MONTHLY}
        GROUP BY category
        ORDER BY net DESC
        LIMIT 1
    """).iloc[0]

    months = df["common_months"] or 1
    return {
        "net_spend": float(df["net_spend"]),
        "cost_of_credit": float(df["cost_of_credit"]),
        "avg_per_month_common": float(df["net_spend_common"]) / months,
        "common_months": int(df["common_months"]),
        "top_category": top["category"],
        "top_category_net": float(top["net"]),
        "txn_count": int(df["txn_count"]),
        "first_date": df["first_date"],
        "last_date": df["last_date"],
    }


def monthly_trend() -> pd.DataFrame:
    """Month x category net spend, categories folded to the fixed top-7 + Other."""
    df = run_query(f"""
        SELECT txn_month, category, SUM(net_spend) AS net_spend
        FROM {MONTHLY}
        GROUP BY txn_month, category
        ORDER BY txn_month, category
    """)
    df["category"] = df["category"].map(fold_to_top7)
    df = (
        df.groupby(["txn_month", "category"], as_index=False)["net_spend"]
        .sum()
    )
    return df


def spend_rollups() -> pd.DataFrame:
    """Net spend by the 5 analytical rollups, ordered for a ranked bar."""
    df = run_query(f"""
        SELECT category_group, SUM(net_amount) AS net_spend, COUNT(*) AS txn_count
        FROM {TXNS}
        GROUP BY category_group
    """)
    df["category_group"] = pd.Categorical(
        df["category_group"], categories=CATEGORY_GROUP_ORDER, ordered=True
    )
    return df.sort_values("net_spend", ascending=False).reset_index(drop=True)


def payment_mix() -> pd.DataFrame:
    """Recorded spend by payment instrument (debits only)."""
    df = run_query(f"""
        SELECT payment_instrument, SUM(amount_inr) AS spend, COUNT(*) AS txn_count
        FROM {TXNS}
        WHERE is_debit
        GROUP BY payment_instrument
        ORDER BY spend DESC
    """)
    df["instrument"] = df["payment_instrument"].map(INSTRUMENT_LABELS)
    return df
