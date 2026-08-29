"""Personal expense tracker — Overview.

Overview page. Reads the Layer 2 views from BigQuery (project + dataset come
from secrets). Explore and Hidden-costs pages are planned.

Run locally:  streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

from lib import queries
from lib.charts import monthly_trend_chart, payment_mix_chart, ranked_bar_chart

st.set_page_config(page_title="Expense Tracker — Overview", page_icon="💸", layout="wide")


def rupees(x: float) -> str:
    return f"₹{x:,.0f}"


def chart_with_table(chart, df, *, caption: str | None = None):
    st.altair_chart(chart, width="stretch", theme="streamlit")
    if caption:
        st.caption(caption)
    with st.expander("Table view"):
        st.dataframe(df, width="stretch", hide_index=True)


st.title("💸 Spend overview")
st.caption(
    "HDFC credit card + Google Pay, Jan–Aug 2026. Amounts are **net** — "
    "reimbursements from friends are subtracted from the category they were "
    "paid into, so P2P totals can look small or negative (that is correct)."
)

# ── Headline KPIs ────────────────────────────────────────────────────────────
k = queries.headline_kpis()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Net spend", rupees(k["net_spend"]),
          help=f'{k["txn_count"]} transactions, {k["first_date"]:%b %Y}–{k["last_date"]:%b %Y}')
c2.metric(f'Avg / month ({k["common_months"]} mo, Feb–Jul)',
          rupees(k["avg_per_month_common"]),
          help="Over the window both sources cover, so the two are comparable.")
c3.metric("Cost of credit", rupees(k["cost_of_credit"]),
          help="Fees & Charges + Debt & EMI, net.")
c4.metric("Top category", k["top_category"],
          help=f'{rupees(k["top_category_net"])} net — '
               f'{k["top_category_net"] / k["net_spend"]:.0%} of all spend')

st.divider()

# ── Monthly spend trend ─────────────────────────────────────────────────────
st.subheader("Monthly spend trend")
trend = queries.monthly_trend()
chart_with_table(
    monthly_trend_chart(trend), trend,
    caption="Debt & EMI are instalments on purchases made before this window — "
            "not new spend in the month they show up.",
)

st.divider()

# ── Spend rollups ───────────────────────────────────────────────────────────
st.subheader("Where it goes — by type of spend")
rollups = queries.spend_rollups()
chart_with_table(
    ranked_bar_chart(rollups, "category_group", "net_spend", "Net spend (₹)"),
    rollups,
)

st.divider()

# ── Payment mix ─────────────────────────────────────────────────────────────
st.subheader("How the money leaves")
mix = queries.payment_mix()
chart_with_table(
    payment_mix_chart(mix), mix[["instrument", "spend", "txn_count"]],
    caption="Recorded spend only. UPI Lite top-ups are netted out of the data, "
            "so this is **not** bank cash-flow.",
)
