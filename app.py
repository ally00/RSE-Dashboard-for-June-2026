"""
Rwanda Stock Exchange — June 2026 Trading Dashboard
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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
DANGER = "#C1121F"
WARN = "#B9770E"
GOOD = "#2E7D32"

COLOR_SEQUENCE = ["#0B2545", "#1B998B", "#D4A017", "#5C80BC", "#8E9AAF",
                   "#C1121F", "#3A5A40", "#7D8CC4"]

st.markdown(f"""
<style>
    .main {{ background-color: #FFFFFF; }}
    h1, h2, h3 {{ color: {PRIMARY}; font-family: 'Segoe UI', sans-serif; }}
    .kpi-card {{
        background-color: {PRIMARY};
        border-left: 5px solid {ACCENT2};
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 8px;
    }}
    .kpi-label {{ font-size: 13px; color: #C9D6E3; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 26px; font-weight: 700; color: #FFFFFF; }}
    .kpi-sub {{ font-size: 12px; color: #9FB3C8; }}
    .alert-box {{
        border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; font-size: 15px;
        color: #FFFFFF;
    }}
    .alert-danger {{ background-color: {DANGER}; }}
    .alert-warn {{ background-color: {WARN}; }}
    .alert-good {{ background-color: {GOOD}; }}
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
    "Type of investment", options=sorted(df_raw["Asset Type"].unique()),
    default=sorted(df_raw["Asset Type"].unique())
)

securities = st.sidebar.multiselect(
    "Company or bond", options=sorted(df_raw["Security Name"].unique()),
    default=[]
)

brokers_all = sorted(set(df_raw["Buyer Code"]).union(set(df_raw["Seller Code"])))
brokers = st.sidebar.multiselect("Broker (buyer or seller)", options=brokers_all, default=[])

st.sidebar.markdown("---")
st.sidebar.caption("Use these filters to narrow down every chart and table on the page. Leave a filter empty to include everything.")

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
    st.warning("No trades match the current filter selection. Please adjust the filters in the sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown("<h1 style='margin-bottom:6px;'>Rwanda Stock Exchange — Trading Dashboard</h1>", unsafe_allow_html=True)
st.markdown("""
<p class='section-note' style='font-size:15px; max-width:900px;'>
The <b>Rwanda Stock Exchange (RSE)</b> is the marketplace where shares of Rwandan companies
(like Bank of Kigali and Bralirwa) and government bonds are bought and sold. This dashboard looks at
every trade recorded on the RSE in <b>June 2026</b> — what was traded, at what price, by which brokers,
and how activity changed day by day — so anyone can see how the market moved during the month.
</p>
""", unsafe_allow_html=True)
st.markdown(f"<p class='section-note'>Dates shown: {df['Posting Date'].min().strftime('%d %b %Y')} – "
            f"{df['Posting Date'].max().strftime('%d %b %Y')} · {len(df)} trades shown "
            f"(out of {len(df_raw)} total in the file)</p>", unsafe_allow_html=True)

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
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Money Traded</div>
        <div class="kpi-value">RWF {total_turnover:,.0f}</div>
        <div class="kpi-sub">Across {len(df)} trades</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Trades</div>
        <div class="kpi-value">{total_deals:,}</div>
        <div class="kpi-sub">{n_securities} different companies/bonds traded</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Units Traded</div>
        <div class="kpi-value">{total_volume:,.0f}</div>
        <div class="kpi-sub">Shares/bond units bought and sold</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Average Trade Size</div>
        <div class="kpi-value">RWF {avg_deal_size:,.0f}</div>
        <div class="kpi-sub">Money traded ÷ number of trades</div></div>""", unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Most Traded (by money value)</div>
        <div class="kpi-value" style="font-size:20px;">{top_security}</div></div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Most Active Broker</div>
        <div class="kpi-value" style="font-size:20px;">{top_broker}</div></div>""", unsafe_allow_html=True)

    # ---- Plain-language market story ----
    st.markdown("### How Did the Market Move This Month?")
    daily_for_story = df.groupby("Posting Date")["Turnover"].sum().sort_index()
    if len(daily_for_story) >= 2:
        mid = len(daily_for_story) // 2
        first_half = daily_for_story.iloc[:mid].sum()
        second_half = daily_for_story.iloc[mid:].sum()
        busiest_day = daily_for_story.idxmax().strftime("%d %B")
        quietest_day = daily_for_story.idxmin().strftime("%d %B")
        if second_half > first_half:
            trend_text = "trading picked up as the month went on, with the second half busier than the first"
        elif second_half < first_half:
            trend_text = "trading slowed down as the month went on, with the first half busier than the second"
        else:
            trend_text = "trading stayed roughly steady through the month"
        st.markdown(f"""
<p class='section-note' style='font-size:15px;'>
Overall, {trend_text}. The busiest trading day was <b>{busiest_day}</b>, while the quietest was
<b>{quietest_day}</b>. <b>{top_security}</b> saw the most money change hands, and broker <b>{top_broker}</b>
was involved in the most trading activity. See the <b>Trends</b> tab for the full day-by-day picture.
</p>
""", unsafe_allow_html=True)

    st.markdown("### Shares vs. Bonds — Where Did the Money Go?")
    split = df.groupby("Asset Type")["Turnover"].sum().reset_index()
    fig = px.pie(split, names="Asset Type", values="Turnover", hole=0.5,
                 color="Asset Type", color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY})
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Note: bonds are usually traded in much larger amounts of money than company shares, "
               "so bonds can dominate this chart even when shares are traded more often. "
               "See Comparisons for a view based on number of trades instead.")

# ============================================================================
# TAB 2 — TRENDS
# ============================================================================
with tabs[1]:
    st.markdown("### Money Traded, Day by Day")
    daily = df.groupby("Posting Date").agg(Turnover=("Turnover", "sum"), Deals=("DEALS", "sum")).reset_index()
    fig = px.line(daily, x="Posting Date", y="Turnover", markers=True,
                  color_discrete_sequence=[PRIMARY])
    fig.update_layout(yaxis_title="Money Traded (RWF)", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("This line shows whether trading activity was rising, falling, or steady across the month.")

    st.markdown("### Number of Trades, Day by Day")
    fig2 = px.bar(daily, x="Posting Date", y="Deals", color_discrete_sequence=[ACCENT])
    fig2.update_layout(yaxis_title="Number of Trades", xaxis_title="Date")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Price Trend for Selected Companies/Bonds")
    price_secs = st.multiselect(
        "Choose what to trace (defaults to the 3 most-traded)",
        options=sorted(df["Security Name"].unique()),
        default=list(df["Security Name"].value_counts().head(3).index)
    )
    if price_secs:
        pdf = df[df["Security Name"].isin(price_secs)].sort_values("Posting Date")
        fig3 = px.line(pdf, x="Posting Date", y="Price", color="Security Name", markers=True)
        fig3.update_layout(yaxis_title="Price", xaxis_title="Date")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Select at least one company or bond above to see its price over the month.")

    st.markdown("### Weekly Totals")
    weekly = df.copy()
    weekly["Week"] = weekly["Posting Date"].dt.to_period("W").astype(str)
    weekly_agg = weekly.groupby(["Week", "Asset Type"])["Turnover"].sum().reset_index()
    fig4 = px.bar(weekly_agg, x="Week", y="Turnover", color="Asset Type", barmode="group",
                  color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY})
    fig4.update_layout(yaxis_title="Money Traded (RWF)")
    st.plotly_chart(fig4, use_container_width=True)

# ============================================================================
# TAB 3 — COMPARISONS
# ============================================================================
with tabs[2]:
    st.markdown("### Shares vs. Bonds, Side by Side")
    comp = df.groupby("Asset Type").agg(
        Turnover=("Turnover", "sum"), Volume=("Quantity", "sum"), Deals=("DEALS", "sum")
    ).reset_index()
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        f = px.bar(comp, x="Asset Type", y="Turnover",
                   color="Asset Type", color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY},
                   title="Money Traded")
        f.update_layout(yaxis_title="RWF")
        st.plotly_chart(f, use_container_width=True)
    with cc2:
        f = px.bar(comp, x="Asset Type", y="Deals",
                   color="Asset Type", color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY},
                   title="Number of Trades")
        st.plotly_chart(f, use_container_width=True)
    with cc3:
        f = px.bar(comp, x="Asset Type", y="Volume",
                   color="Asset Type", color_discrete_map={"Equity": ACCENT, "Bond": PRIMARY},
                   title="Units Traded")
        st.plotly_chart(f, use_container_width=True)
    st.caption("Bonds usually involve far more money per trade than shares, so comparing 'Number of Trades' "
               "gives a fairer sense of which market was more active day-to-day.")

    st.markdown("### Top 10 Most-Traded Companies/Bonds")
    top10 = df.groupby("Security Name")["Turnover"].sum().nlargest(10).reset_index()
    fig5 = px.bar(top10.sort_values("Turnover"), x="Turnover", y="Security Name", orientation="h",
                  color_discrete_sequence=[ACCENT2])
    fig5.update_layout(xaxis_title="Money Traded (RWF)", yaxis_title="")
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### Broker Buying vs. Selling")
    buy = df.groupby("Buyer Code")["Turnover"].sum().rename("Bought")
    sell = df.groupby("Seller Code")["Turnover"].sum().rename("Sold")
    broker_cmp = pd.concat([buy, sell], axis=1).fillna(0).reset_index().rename(columns={"index": "Broker"})
    broker_cmp_melt = broker_cmp.melt(id_vars="Broker", var_name="Side", value_name="Turnover")
    fig6 = px.bar(broker_cmp_melt, x="Broker", y="Turnover", color="Side", barmode="group",
                  color_discrete_map={"Bought": ACCENT, "Sold": PRIMARY})
    fig6.update_layout(yaxis_title="Money (RWF)")
    st.plotly_chart(fig6, use_container_width=True)
    st.caption("Each bar shows how much money a broker's clients spent buying (teal) versus how much they "
               "received selling (navy) during the month.")

# ============================================================================
# TAB 4 — DISTRIBUTIONS
# ============================================================================
with tabs[3]:
    st.markdown("### Busiest Trading Days of the Week")
    dow = df.copy()
    dow["Day of Week"] = dow["Posting Date"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_counts = dow.groupby("Day of Week")["DEALS"].sum().reindex(order).dropna().reset_index()
    fig_dow = px.bar(dow_counts, x="Day of Week", y="DEALS", color_discrete_sequence=[ACCENT])
    fig_dow.update_layout(yaxis_title="Number of Trades", xaxis_title="")
    st.plotly_chart(fig_dow, use_container_width=True)
    st.caption("This shows which days of the week tend to see the most trading — useful for spotting a "
               "weekly pattern at a glance.")

    st.markdown("### Price Range by Company (Shares Only)")
    eq = df[df["Asset Type"] == "Equity"]
    if not eq.empty:
        fig8 = px.box(eq, x="Security Name", y="Price", color="Security Name")
        fig8.update_layout(showlegend=False, xaxis_title="", yaxis_title="Price")
        st.plotly_chart(fig8, use_container_width=True)
        st.caption("Each box shows the typical price range a share traded at during the month — a taller "
                   "box means the price moved around more.")
    else:
        st.info("No share trades in the current filter selection.")

    st.markdown("### Number of Trades per Company/Bond")
    deals_sec = df.groupby("Security Name")["DEALS"].sum().sort_values(ascending=False).reset_index()
    fig9 = px.bar(deals_sec, x="Security Name", y="DEALS", color_discrete_sequence=[ACCENT2])
    fig9.update_layout(xaxis_tickangle=-45, xaxis_title="", yaxis_title="Number of Trades")
    st.plotly_chart(fig9, use_container_width=True)

# ============================================================================
# TAB 5 — ALERTS
# ============================================================================
with tabs[4]:
    st.markdown("### Things Worth Your Attention")

    st.markdown(f"""<div class="alert-box alert-warn">
    <b>Data was cleaned before analysis:</b> the original file had one summary row and two broker codes typed
    incorrectly (<code>B10</code> and <code>BRK10</code>, both corrected to <code>BR10</code>). These were fixed
    automatically so they wouldn't skew the numbers.
    </div>""", unsafe_allow_html=True)

    # Broker spread
    broker_turnover = pd.concat([
        df.groupby("Buyer Code")["Turnover"].sum(),
        df.groupby("Seller Code")["Turnover"].sum()
    ]).groupby(level=0).sum().sort_values(ascending=False)
    top_share = broker_turnover.iloc[0] / broker_turnover.sum() * 100
    if top_share > 40:
        st.markdown(f"""<div class="alert-box alert-danger"><b>One broker dominates trading:</b>
        broker <b>{broker_turnover.index[0]}</b> was involved in <b>{top_share:.1f}%</b> of all money traded
        in this selection. That's a large share for one broker to hold.</div>""", unsafe_allow_html=True)
    elif top_share > 25:
        st.markdown(f"""<div class="alert-box alert-warn"><b>Trading is a bit uneven between brokers:</b>
        broker <b>{broker_turnover.index[0]}</b> handled <b>{top_share:.1f}%</b> of all money traded.</div>""",
        unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="alert-box alert-good"><b>Trading is well spread out:</b>
        no single broker handled more than a quarter of all money traded (top broker: {top_share:.1f}%).</div>""",
        unsafe_allow_html=True)

    # Large trades
    thresh = df["Turnover"].quantile(0.95)
    large_trades = df[df["Turnover"] >= thresh].sort_values("Turnover", ascending=False)
    st.markdown(f"""<div class="alert-box alert-warn"><b>{len(large_trades)} unusually large trades found</b>
    (the biggest 5%, each worth RWF {thresh:,.0f} or more) — these are mostly big bond trades, which is normal,
    but worth a quick look.</div>""", unsafe_allow_html=True)
    st.dataframe(large_trades[["Posting Date","Security Name","Asset Type","Buyer Code","Seller Code","Quantity","Price","Turnover"]],
                 use_container_width=True, hide_index=True)

    # Rarely traded
    low_liquidity = df.groupby("Security Name")["DEALS"].sum().sort_values()
    low_liquidity = low_liquidity[low_liquidity <= 1]
    if len(low_liquidity) > 0:
        st.markdown(f"""<div class="alert-box alert-warn"><b>Rarely-traded companies/bonds:</b>
        {len(low_liquidity)} of them only traded once all month: {', '.join(low_liquidity.index[:10])}
        {'...' if len(low_liquidity) > 10 else ''}</div>""", unsafe_allow_html=True)

# ============================================================================
# TAB 6 — DATA EXPLORER
# ============================================================================
with tabs[5]:
    st.markdown("### Look Through Every Trade")
    search = st.text_input("Search (company, bond, or broker code)", "")
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
    st.download_button("⬇️ Download this table as CSV", data=csv, file_name="rse_filtered_trades.csv", mime="text/csv")

# ============================================================================
# TAB 7 — ETHICS & INSIGHTS
# ============================================================================
with tabs[6]:
    st.markdown("### How Fair and Balanced Is the Trading?")
    shares = (broker_turnover / broker_turnover.sum())
    hhi = (shares ** 2).sum() * 10000
    if hhi > 2500:
        level, tone = "Trading is concentrated in a few brokers", "alert-danger"
    elif hhi > 1500:
        level, tone = "Trading is somewhat concentrated", "alert-warn"
    else:
        level, tone = "Trading is well spread out across brokers", "alert-good"
    st.markdown(f"""<div class="alert-box {tone}"><b>{level}.</b> The top broker
    (<b>{broker_turnover.index[0]}</b>) handled about <b>{top_share:.0f}%</b> of the money traded this month.
    A healthier market usually has trading spread across many brokers rather than a few.</div>""",
    unsafe_allow_html=True)

    st.markdown("### Fairness Notes")
    st.markdown("""
- **Broker names are hidden.** We only see broker codes (like BR9, BR10), not company names. This protects
  privacy but means we can't say *why* one broker is more active than another.
- **Some companies and bonds barely trade.** A few only had one trade all month. When something trades
  rarely, its price is less reliable, and it can be harder for smaller investors to buy or sell it easily.
- **This is only one month of data.** Patterns seen here should be checked against other months before
  drawing firm conclusions.
- **Shares and bonds shouldn't be compared by money value alone.** Bonds trade in much larger amounts of
  money than shares, so comparing them by number of trades is fairer than comparing them by money value.
    """)

    st.markdown("### Key Takeaways")
    n_rare = df.groupby("Security Name")["DEALS"].sum().le(1).sum()
    insights = [
        f"**{top_security}** had the most money traded this month, alongside strong activity in several bonds.",
        f"Broker activity was {'uneven, with one broker standing out' if hhi > 1500 else 'fairly balanced across brokers'}.",
        f"{n_rare} companies or bonds only traded once all month — a small group of names does most of the trading.",
        "A handful of very large bond trades account for a big share of total money traded — worth viewing "
        "separately from regular share trading.",
    ]
    for i in insights:
        st.markdown(f"- {i}")

# ============================================================================
# TAB 8 — RECOMMENDATIONS
# ============================================================================
with tabs[7]:
    st.markdown("### What Could Be Done Next")
    st.markdown(f"""
1. **Keep an eye on broker balance.** Right now the top broker handles about {top_share:.0f}% of trading —
   worth watching whether more brokers become active over time.
2. **Report shares and bonds separately.** Mixing them together in money totals makes bonds look far more
   important than they are — use number of trades when comparing the two fairly.
3. **Review the biggest trades each month.** A short manual check of the largest trades helps catch data
   entry mistakes early and highlights real market-moving events.
4. **Look into companies/bonds that barely trade.** They may need more attention from investors, better
   information, or incentives to encourage more buying and selling.
5. **Improve data entry.** Two broker codes were typed incorrectly this month. Using a dropdown list instead
   of free typing would prevent this kind of mistake.
6. **Track more months over time.** One month only shows so much — adding more months would make it possible
   to see real trends and seasonal patterns, not just a single snapshot.
    """)
    st.info("💡 Tip: use the sidebar filters to re-run this whole dashboard — including these numbers — "
            "on any date range, type of investment, company/bond, or broker.")
