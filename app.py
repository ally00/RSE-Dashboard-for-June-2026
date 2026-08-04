"""
Rwanda Stock Exchange — June 2026 Trading Dashboard
Author: Built for Ally (Kepler College)
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="RSE Trading Dashboard — June 2026",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# THEME / CSS
# ----------------------------------------------------------------------------
PRIMARY = "#0B2545"      # deep navy
ACCENT = "#1B998B"       # teal
ACCENT2 = "#D4A017"      # muted gold
BG_CARD = "#F4F7FB"
DANGER = "#C1121F"
WARN = "#E09F3E"
GOOD = "#2E7D32"

COLOR_SEQUENCE = ["#0B2545", "#1B998B", "#D4A017", "#5C80BC", "#8E9AAF",
                   "#C1121F", "#3A5A40", "#7D8CC4"]

st.markdown(f"""
<style>
    .main {{ background-color: #FFFFFF; }}
    h1, h2, h3 {{ color: {PRIMARY}; font-family: 'Segoe UI', sans-serif; }}
    .kpi-card {{
        background-color: {BG_CARD};
        border-left: 5px solid {ACCENT};
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 8px;
    }}
    .kpi-label {{ font-size: 13px; color: #5A6472; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 26px; font-weight: 700; color: {PRIMARY}; }}
    .kpi-sub {{ font-size: 12px; color: #8E9AAF; }}
    .alert-box {{
        border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; font-size: 14px;
    }}
    .alert-danger {{ background-color: #FDECEC; border-left: 5px solid {DANGER}; }}
    .alert-warn {{ background-color: #FEF6E7; border-left: 5px solid {WARN}; }}
    .alert-good {{ background-color: #EAF5EA; border-left: 5px solid {GOOD}; }}
    .section-note {{ color: #5A6472; font-size: 14px; }}
    div[data-testid="stMetricValue"] {{ color: {PRIMARY}; }}
</style>
""", unsafe_allow_html=True)

px.defaults.color_discrete_sequence = COLOR_SEQUENCE
px.defaults.template = "plotly_white"

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("rse_june2026_clean.csv", parse_dates=["Posting Date"])
    return df

df_raw = load_data()

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 📈 RSE Dashboard")
st.sidebar.caption("Rwanda Stock Exchange · June 2026")
st.sidebar.markdown("---")

min_date, max_date = df_raw["Posting Date"].min(), df_raw["Posting Date"].max()
date_range = st.sidebar.date_input(
    "Trading date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

asset_types = st.sidebar.multiselect(
    "Asset type", options=sorted(df_raw["Asset Type"].unique()),
    default=sorted(df_raw["Asset Type"].unique())
)

securities = st.sidebar.multiselect(
    "Security", options=sorted(df_raw["Security Name"].unique()),
    default=[]
)

brokers_all = sorted(set(df_raw["Buyer Code"]).union(set(df_raw["Seller Code"])))
brokers = st.sidebar.multiselect("Broker (buyer or seller)", options=brokers_all, default=[])

st.sidebar.markdown("---")
st.sidebar.caption("Use the filters above to narrow every chart and table on this page. Leave a filter empty to include all values.")

# Apply filters
df = df_raw[
    (df_raw["Posting Date"] >= pd.to_datetime(start_date)) &
    (df_raw["Posting Date"] <= pd.to_datetime(end_date)) &
    (df_raw["Asset Type"].isin(asset_types))
].copy()

if securities:
    df = df[df["Security Name"].isin(securities)]
if brokers:
    df = df[df["Buyer Code"].isin(brokers) | df["Seller Code"].isin(brokers)]

if df.empty:
    st.warning("No trades match the current filter selection. Adjust the filters in the sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown(f"<h1 style='margin-bottom:0;'>Rwanda Stock Exchange — Trading Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='section-note'>Period covered: {df['Posting Date'].min().strftime('%d %b %Y')} – "
            f"{df['Posting Date'].max().strftime('%d %b %Y')} · {len(df)} trades shown "
            f"(of {len(df_raw)} total in source file)</p>", unsafe_allow_html=True)

tabs = st.tabs([
    "🏠 Overview & KPIs", "📈 Trends", "⚖️ Comparisons", "📊 Distributions",
    "🚨 Alerts", "🔍 Data Explorer", "🧭 Ethics & Insights", "✅ Recommendations"
])

# ============================================================================
# TAB 1 — OVERVIEW & KPIs
# ============================================================================
with tabs[0]:
    total_turnover = df["Turnover"].sum()
    total_deals = int(df["DEALS"].sum())
    total_volume = df["Quantity"].sum()
    n_securities = df["Security"].nunique()
    avg_deal_size = total_turnover / total_deals if total_deals else 0
    top_security = df.groupby("Security Name")["Turnover"].sum().idxmax()
    top_broker_series = pd.concat([
        df.groupby("Buyer Code")["Turnover"].sum(),
        df.groupby("Seller Code")["Turnover"].sum()
    ]).groupby(level=0).sum()
    top_broker = top_broker_series.idxmax()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Turnover</div>
        <div class="kpi-value">RWF {total_turnover:,.0f}</div>
        <div class="kpi-sub">Across {len(df)} trades</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Deals</div>
        <div class="kpi-value">{total_deals:,}</div>
        <div class="kpi-sub">{n_securities} securities traded</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Volume</div>
        <div class="kpi-value">{total_volume:,.0f}</div>
        <div class="kpi-sub">Units traded</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Avg. Deal Size</div>
        <div class="kpi-value">RWF {avg_deal_size:,.0f}</div>
        <div class="kpi-sub">Turnover ÷ deals</div></div>""", unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Most Traded Security (by turnover)</div>
        <div class="kpi-value" style="font-size:20px;">{top_security}</div></div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Most Active Broker (by turnover)</div>
        <div class="kpi-value" style="font-size:20px;">{top_broker}</div></div>""", unsafe_allow_html=True)

    st.markdown("### Turnover Split — Equity vs. Bond")
    split = df.groupby("Asset Type")["Turnover"].sum().reset_index()
    fig = px.pie(split, names="Asset Type", values="Turnover", hole=0.5,
                 color="Asset Type", color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY})
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Note: bond quantities are face values (often in the billions of RWF), so bond turnover naturally dwarfs equity turnover even when equities see more individual deals. See the Comparisons tab for a deal-count view.")

# ============================================================================
# TAB 2 — TRENDS
# ============================================================================
with tabs[1]:
    st.markdown("### Daily Turnover Trend")
    daily = df.groupby("Posting Date").agg(Turnover=("Turnover", "sum"), Deals=("DEALS", "sum")).reset_index()
    fig = px.line(daily, x="Posting Date", y="Turnover", markers=True,
                  color_discrete_sequence=[PRIMARY])
    fig.update_layout(yaxis_title="Turnover (RWF)", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Daily Number of Deals")
    fig2 = px.bar(daily, x="Posting Date", y="Deals", color_discrete_sequence=[ACCENT])
    fig2.update_layout(yaxis_title="Deals", xaxis_title="Date")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Price Trend by Security")
    price_secs = st.multiselect(
        "Choose securities to trace (defaults to top 3 by trade count)",
        options=sorted(df["Security Name"].unique()),
        default=list(df["Security Name"].value_counts().head(3).index)
    )
    if price_secs:
        pdf = df[df["Security Name"].isin(price_secs)].sort_values("Posting Date")
        fig3 = px.line(pdf, x="Posting Date", y="Price", color="Security Name", markers=True)
        fig3.update_layout(yaxis_title="Price", xaxis_title="Date")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Select at least one security above to see its price trend.")

    st.markdown("### Weekly Turnover Summary")
    weekly = df.copy()
    weekly["Week"] = weekly["Posting Date"].dt.to_period("W").astype(str)
    weekly_agg = weekly.groupby(["Week", "Asset Type"])["Turnover"].sum().reset_index()
    fig4 = px.bar(weekly_agg, x="Week", y="Turnover", color="Asset Type", barmode="group",
                  color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY})
    st.plotly_chart(fig4, use_container_width=True)

# ============================================================================
# TAB 3 — COMPARISONS
# ============================================================================
with tabs[2]:
    st.markdown("### Equity vs. Bond — Turnover, Volume & Deal Count")
    comp = df.groupby("Asset Type").agg(
        Turnover=("Turnover", "sum"), Volume=("Quantity", "sum"), Deals=("DEALS", "sum")
    ).reset_index()
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.plotly_chart(px.bar(comp, x="Asset Type", y="Turnover",
                                color="Asset Type", color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY},
                                title="Turnover"), use_container_width=True)
    with cc2:
        st.plotly_chart(px.bar(comp, x="Asset Type", y="Deals",
                                color="Asset Type", color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY},
                                title="Deal Count"), use_container_width=True)
    with cc3:
        st.plotly_chart(px.bar(comp, x="Asset Type", y="Volume",
                                color="Asset Type", color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY},
                                title="Volume"), use_container_width=True)

    st.markdown("### Top 10 Securities by Turnover")
    top10 = df.groupby("Security Name")["Turnover"].sum().nlargest(10).reset_index()
    fig5 = px.bar(top10.sort_values("Turnover"), x="Turnover", y="Security Name", orientation="h",
                  color_discrete_sequence=[ACCENT2])
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### Broker Activity — Buy vs. Sell Turnover")
    buy = df.groupby("Buyer Code")["Turnover"].sum().rename("Buy Turnover")
    sell = df.groupby("Seller Code")["Turnover"].sum().rename("Sell Turnover")
    broker_cmp = pd.concat([buy, sell], axis=1).fillna(0).reset_index().rename(columns={"index": "Broker"})
    broker_cmp_melt = broker_cmp.melt(id_vars="Broker", var_name="Side", value_name="Turnover")
    fig6 = px.bar(broker_cmp_melt, x="Broker", y="Turnover", color="Side", barmode="group",
                  color_discrete_map={"Buy Turnover": ACCENT, "Sell Turnover": PRIMARY})
    st.plotly_chart(fig6, use_container_width=True)

# ============================================================================
# TAB 4 — DISTRIBUTIONS
# ============================================================================
with tabs[3]:
    st.markdown("### Distribution of Deal (Turnover) Sizes")
    fig7 = px.histogram(df, x="Turnover", color="Asset Type", nbins=40, marginal="box",
                         color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY})
    fig7.update_layout(bargap=0.05)
    st.plotly_chart(fig7, use_container_width=True)
    st.caption("Bond and equity turnover sit on very different scales — filter to a single asset type in the sidebar for a cleaner read of one group's spread.")

    st.markdown("### Price Distribution by Security (Equities only)")
    eq = df[df["Asset Type"] == "Equity"]
    if not eq.empty:
        fig8 = px.box(eq, x="Security Name", y="Price", color="Security Name")
        fig8.update_layout(showlegend=False)
        st.plotly_chart(fig8, use_container_width=True)
    else:
        st.info("No equity trades in the current filter selection.")

    st.markdown("### Deals per Security")
    deals_sec = df.groupby("Security Name")["DEALS"].sum().sort_values(ascending=False).reset_index()
    fig9 = px.bar(deals_sec, x="Security Name", y="DEALS", color_discrete_sequence=[ACCENT2])
    fig9.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig9, use_container_width=True)

# ============================================================================
# TAB 5 — ALERTS
# ============================================================================
with tabs[4]:
    st.markdown("### Automated Alerts")

    # Data-quality alerts (computed on raw data, informational)
    st.markdown(f"""<div class="alert-box alert-warn">
    <b>Data quality — cleaned on load:</b> the source file contained a summary/totals row and two broker-code typos
    (<code>B10</code> → <code>BR10</code>, <code>BRK10</code> → <code>BR10</code>), which were corrected before analysis.
    </div>""", unsafe_allow_html=True)

    # Concentration risk — top broker share
    broker_turnover = pd.concat([
        df.groupby("Buyer Code")["Turnover"].sum(),
        df.groupby("Seller Code")["Turnover"].sum()
    ]).groupby(level=0).sum().sort_values(ascending=False)
    top_share = broker_turnover.iloc[0] / broker_turnover.sum() * 100
    if top_share > 40:
        st.markdown(f"""<div class="alert-box alert-danger"><b>High concentration risk:</b>
        broker <b>{broker_turnover.index[0]}</b> accounts for <b>{top_share:.1f}%</b> of turnover in the current selection —
        above the 40% watch threshold.</div>""", unsafe_allow_html=True)
    elif top_share > 25:
        st.markdown(f"""<div class="alert-box alert-warn"><b>Moderate concentration:</b>
        broker <b>{broker_turnover.index[0]}</b> accounts for <b>{top_share:.1f}%</b> of turnover.</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="alert-box alert-good"><b>Healthy distribution:</b>
        no single broker exceeds 25% of turnover (top broker: {top_share:.1f}%).</div>""", unsafe_allow_html=True)

    # Large single trades (outliers)
    thresh = df["Turnover"].quantile(0.95)
    large_trades = df[df["Turnover"] >= thresh].sort_values("Turnover", ascending=False)
    st.markdown(f"""<div class="alert-box alert-warn"><b>{len(large_trades)} large trades flagged</b>
    (top 5% by turnover, ≥ RWF {thresh:,.0f}) — mostly bond block trades, which is expected given bond face values.
    Review below.</div>""", unsafe_allow_html=True)
    st.dataframe(large_trades[["Posting Date","Security Name","Asset Type","Buyer Code","Seller Code","Quantity","Price","Turnover"]],
                 use_container_width=True, hide_index=True)

    # Thinly traded securities
    low_liquidity = df.groupby("Security Name")["DEALS"].sum().sort_values()
    low_liquidity = low_liquidity[low_liquidity <= 1]
    if len(low_liquidity) > 0:
        st.markdown(f"""<div class="alert-box alert-warn"><b>Low-liquidity watch:</b>
        {len(low_liquidity)} securities recorded only a single deal in this period: {', '.join(low_liquidity.index[:10])}
        {'...' if len(low_liquidity) > 10 else ''}</div>""", unsafe_allow_html=True)

# ============================================================================
# TAB 6 — DATA EXPLORER
# ============================================================================
with tabs[5]:
    st.markdown("### Explore the Filtered Dataset")
    search = st.text_input("Search (security, broker code)", "")
    view = df.copy()
    if search:
        mask = (view["Security Name"].str.contains(search, case=False, na=False) |
                view["Security"].str.contains(search, case=False, na=False) |
                view["Buyer Code"].str.contains(search, case=False, na=False) |
                view["Seller Code"].str.contains(search, case=False, na=False))
        view = view[mask]

    sort_col = st.selectbox("Sort by", options=["Posting Date","Turnover","Quantity","Price","DEALS"], index=0)
    ascending = st.checkbox("Ascending", value=False)
    view = view.sort_values(sort_col, ascending=ascending)

    st.dataframe(
        view[["Posting Date","Security Name","Asset Type","Buyer Code","Seller Code","Quantity","Price","Turnover","DEALS"]],
        use_container_width=True, hide_index=True
    )
    st.caption(f"Showing {len(view)} of {len(df)} filtered trades.")

    csv = view.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download this view as CSV", data=csv, file_name="rse_filtered_trades.csv", mime="text/csv")

# ============================================================================
# TAB 7 — ETHICS & INSIGHTS
# ============================================================================
with tabs[6]:
    st.markdown("### Market Concentration (HHI-style measure)")
    shares = (broker_turnover / broker_turnover.sum())
    hhi = (shares ** 2).sum() * 10000  # standard HHI scale 0-10,000
    st.metric("Herfindahl-Hirschman Index (brokers, by turnover)", f"{hhi:,.0f}")
    if hhi > 2500:
        level, tone = "Highly concentrated", "alert-danger"
    elif hhi > 1500:
        level, tone = "Moderately concentrated", "alert-warn"
    else:
        level, tone = "Competitive / unconcentrated", "alert-good"
    st.markdown(f"""<div class="alert-box {tone}"><b>{level}</b> market structure based on standard
    HHI thresholds (US DOJ/FTC guidelines: &lt;1500 unconcentrated, 1500–2500 moderate, &gt;2500 high).</div>""",
    unsafe_allow_html=True)

    st.markdown("### Fairness & Transparency Notes")
    st.markdown("""
- **Broker anonymity**: broker codes (e.g. BR9, BR10) are used rather than firm names, which is appropriate for
  a public-facing dashboard but limits accountability analysis — a regulator view would need the code-to-firm mapping.
- **Liquidity access**: several bonds and small-cap equities show only one deal all month. Thin markets can make it
  harder for smaller investors to enter or exit positions at fair prices, and prices from a single trade are less
  reliable indicators of fair value.
- **Data completeness**: this file covers one month only; concentration and liquidity conclusions should be
  checked against a longer history before being treated as durable patterns.
- **Bond vs. equity comparability**: because bond turnover reflects face value, blending bond and equity turnover
  in a single ranking (e.g. "top securities") can overstate bond importance relative to trading activity — deal
  count is a fairer cross-asset comparison than turnover.
    """)

    st.markdown("### Key Insights Summary")
    insights = [
        f"**{top_security}** led turnover in the selected period, alongside heavy bond activity in long-dated FXD issues.",
        f"Brokers show {'uneven' if hhi > 1500 else 'reasonably balanced'} participation (HHI = {hhi:,.0f}).",
        f"{len(low_liquidity) if 'low_liquidity' in dir() else df.groupby('Security Name')['DEALS'].sum().le(1).sum()} securities traded only once, "
        "suggesting a long tail of illiquid instruments alongside a few very active names.",
        "Large bond trades (block trades) are the main driver of extreme turnover values — treat them separately from equity activity when benchmarking.",
    ]
    for i in insights:
        st.markdown(f"- {i}")

# ============================================================================
# TAB 8 — RECOMMENDATIONS
# ============================================================================
with tabs[7]:
    st.markdown("### Recommendations")
    st.markdown(f"""
1. **Monitor broker concentration.** With an HHI of {hhi:,.0f}, keep tracking whether trading activity broadens
   over time or continues concentrating among a small set of brokers.
2. **Separate equity and bond reporting.** Because bond face values distort blended turnover figures, report
   equity and bond activity on separate scales (or use deal count) in any executive summary.
3. **Flag and review large block trades individually.** The top 5% of trades by turnover disproportionately shape
   monthly totals; a short manual review of these each month would catch data errors early and surface real
   market-moving events.
4. **Investigate thinly-traded securities.** Single-deal securities may need liquidity-support measures (e.g.
   market-maker incentives) or simply reflect low investor awareness worth addressing through outreach.
5. **Tighten data entry controls.** The two broker-code typos found this month (`B10`, `BRK10`) suggest a
   validation step (dropdown/lookup instead of free text) at the point of data entry would reduce cleanup effort.
6. **Track trends monthly.** A single month of data limits trend conclusions — extending this dashboard to ingest
   multiple months (stacking CSVs) would allow real month-over-month and seasonal analysis.
    """)
    st.info("💡 Tip: use the sidebar filters to re-run this whole dashboard — including these recommendations' "
            "underlying numbers — on any subset of dates, asset types, securities, or brokers.")

st.markdown("---")
st.caption("Built with Streamlit & Plotly · Data: Rwanda Stock Exchange, June 2026 · Dashboard for academic use.")
