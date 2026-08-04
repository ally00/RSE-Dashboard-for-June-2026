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
    .definition-box {{
        background: linear-gradient(135deg, {PRIMARY} 0%, #143a63 100%);
        border-left: 6px solid {ACCENT2};
        border-radius: 10px;
        padding: 22px 28px;
        margin: 10px 0 18px 0;
        color: #FFFFFF;
    }}
    .definition-box .quote-mark {{
        font-size: 42px; color: {ACCENT2}; line-height: 0; position: relative; top: 18px;
        font-family: Georgia, serif;
    }}
    .definition-box p {{ font-size: 16px; line-height: 1.6; margin: 0 0 6px 0; font-style: italic; }}
    .definition-box .source {{ font-size: 13px; color: #C9D6E3; font-style: normal; text-align: right; }}
    .glossary-term {{
        background-color: #F4F7FB; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;
        border-left: 4px solid {ACCENT};
    }}
    .glossary-term b {{ color: {PRIMARY}; }}
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
df_raw["Security Class"] = df_raw["Asset Type"].map({"Equity": "Equity Security", "Bond": "Debt Security"})

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 📈 RSE Dashboard")
st.sidebar.caption("Rwanda Stock Exchange · June 2026")
st.sidebar.markdown("---")

min_date, max_date = df_raw["Posting Date"].min(), df_raw["Posting Date"].max()
date_range = st.sidebar.date_input(
    "Posting Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

asset_types = st.sidebar.multiselect(
    "Security Type", options=sorted(df_raw["Asset Type"].unique()),
    default=sorted(df_raw["Asset Type"].unique())
)

securities = st.sidebar.multiselect(
    "Security (Ticker / Name)", options=sorted(df_raw["Security Name"].unique()),
    default=[]
)

brokers_all = sorted(set(df_raw["Buyer Code"]).union(set(df_raw["Seller Code"])))
brokers = st.sidebar.multiselect("Broker Code (Buyer Code / Seller Code)", options=brokers_all, default=[])

st.sidebar.markdown("---")
st.sidebar.caption("Filters apply across all tabs. Leave a filter empty to include the full universe of securities.")

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
<div class="definition-box">
<span class="quote-mark">&#8220;</span>
<p>The Rwanda Stock Exchange Ltd. was established to promote and manage the business of a securities
exchange which include among others to provide a platform for the trading of securities with the purpose
of carrying out stock market operations, named "the Exchange".</p>
<div class="source">— Rwanda Stock Exchange Ltd.</div>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<p class='section-note' style='font-size:15px; max-width:900px;'>
This dashboard analyzes every trade executed on the Exchange in <b>June 2026</b>, covering <b>Posting Date</b>,
<b>Security</b>, <b>Buyer Code</b>, <b>Seller Code</b>, <b>Quantity</b>, <b>Price</b>, <b>Turnover</b>, and
<b>Deals</b> for each transaction across both Equity and Debt Securities listed on the Exchange.
</p>
""", unsafe_allow_html=True)
st.markdown(f"<p class='section-note'>Posting Date range: {df['Posting Date'].min().strftime('%d %b %Y')} – "
            f"{df['Posting Date'].max().strftime('%d %b %Y')} · {len(df)} deals shown "
            f"(of {len(df_raw)} total in the dataset)</p>", unsafe_allow_html=True)

tabs = st.tabs([
    "🏠 Overview & KPIs", "📈 Trends", "⚖️ Comparisons", "📊 Distributions",
    "🚨 Alerts", "🔍 Data Explorer", "🧭 Ethics & Insights", "📖 Glossary", "✅ Recommendations"
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
    top_ticker = df.groupby("Security")["Turnover"].sum().idxmax()
    top_broker_series = pd.concat([
        df.groupby("Buyer Code")["Turnover"].sum(),
        df.groupby("Seller Code")["Turnover"].sum()
    ]).groupby(level=0).sum()
    top_broker = top_broker_series.idxmax()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Turnover</div>
        <div class="kpi-value">RWF {total_turnover:,.0f}</div>
        <div class="kpi-sub">Σ (Price × Quantity) across {len(df)} deals</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Deals</div>
        <div class="kpi-value">{total_deals:,}</div>
        <div class="kpi-sub">{n_securities} securities traded</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Volume</div>
        <div class="kpi-value">{total_volume:,.0f}</div>
        <div class="kpi-sub">Σ Quantity (units)</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Average Turnover per Deal</div>
        <div class="kpi-value">RWF {avg_deal_size:,.0f}</div>
        <div class="kpi-sub">Turnover ÷ Deals</div></div>""", unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Leading Security (by Turnover)</div>
        <div class="kpi-value" style="font-size:20px;">{top_ticker} — {top_security}</div></div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Leading Counterparty (Broker Code)</div>
        <div class="kpi-value" style="font-size:20px;">{top_broker}</div></div>""", unsafe_allow_html=True)

    # ---- Market commentary ----
    st.markdown("### Market Commentary — Session Activity Over the Month")
    daily_for_story = df.groupby("Posting Date")["Turnover"].sum().sort_index()
    if len(daily_for_story) >= 2:
        mid = len(daily_for_story) // 2
        first_half = daily_for_story.iloc[:mid].sum()
        second_half = daily_for_story.iloc[mid:].sum()
        busiest_day = daily_for_story.idxmax().strftime("%d %B")
        quietest_day = daily_for_story.idxmin().strftime("%d %B")
        if second_half > first_half:
            trend_text = "Turnover trended upward, with the second half of the month recording higher cumulative Turnover than the first"
        elif second_half < first_half:
            trend_text = "Turnover trended downward, with the first half of the month recording higher cumulative Turnover than the second"
        else:
            trend_text = "Turnover remained broadly flat across the month"
        st.markdown(f"""
<p class='section-note' style='font-size:15px;'>
{trend_text}. The highest single-session Turnover was recorded on <b>{busiest_day}</b>, while the lowest was
recorded on <b>{quietest_day}</b>. <b>{top_ticker} ({top_security})</b> was the leading security by Turnover,
and Broker Code <b>{top_broker}</b> was the most active counterparty across both sides of the market.
Full session-by-session detail is available under the <b>Trends</b> tab.
</p>
""", unsafe_allow_html=True)

    st.markdown("### Turnover Composition — Equity vs. Debt Securities")
    split = df.groupby("Security Class")["Turnover"].sum().reset_index()
    fig = px.pie(split, names="Security Class", values="Turnover", hole=0.5,
                 color="Security Class", color_discrete_map={"Equity Security": ACCENT, "Debt Security": PRIMARY})
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Debt Securities are typically transacted at much higher face values than Equity Securities, "
               "so Turnover composition can overstate the relative activity of the bond market. See "
               "Comparisons for a Deal-count basis instead.")

# ============================================================================
# TAB 2 — TRENDS
# ============================================================================
with tabs[1]:
    st.markdown("### Turnover Trend (Daily, by Posting Date)")
    daily = df.groupby("Posting Date").agg(Turnover=("Turnover", "sum"), Deals=("DEALS", "sum")).reset_index()
    fig = px.line(daily, x="Posting Date", y="Turnover", markers=True,
                  color_discrete_sequence=[PRIMARY])
    fig.update_layout(yaxis_title="Turnover (RWF)", xaxis_title="Posting Date")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Session-level Turnover trend across the reporting period.")

    st.markdown("### Deal Count Trend (Daily, by Posting Date)")
    fig2 = px.bar(daily, x="Posting Date", y="Deals", color_discrete_sequence=[ACCENT])
    fig2.update_layout(yaxis_title="Deals", xaxis_title="Posting Date")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Price Trend by Security")
    price_secs = st.multiselect(
        "Select securities to trace (defaults to the 3 with highest Deal count)",
        options=sorted(df["Security Name"].unique()),
        default=list(df["Security Name"].value_counts().head(3).index)
    )
    if price_secs:
        pdf = df[df["Security Name"].isin(price_secs)].sort_values("Posting Date")
        fig3 = px.line(pdf, x="Posting Date", y="Price", color="Security Name", markers=True)
        fig3.update_layout(yaxis_title="Price", xaxis_title="Posting Date")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Select at least one security above to view its Price trend across the reporting period.")

    st.markdown("### Weekly Turnover by Security Type")
    weekly = df.copy()
    weekly["Week"] = weekly["Posting Date"].dt.to_period("W").astype(str)
    weekly_agg = weekly.groupby(["Week", "Security Class"])["Turnover"].sum().reset_index()
    fig4 = px.bar(weekly_agg, x="Week", y="Turnover", color="Security Class", barmode="group",
                  color_discrete_map={"Equity Security": ACCENT, "Debt Security": PRIMARY})
    fig4.update_layout(yaxis_title="Turnover (RWF)")
    st.plotly_chart(fig4, use_container_width=True)

# ============================================================================
# TAB 3 — COMPARISONS
# ============================================================================
with tabs[2]:
    st.markdown("### Securities by Type — Turnover, Volume & Deals")
    comp = df.groupby("Security Class").agg(
        Turnover=("Turnover", "sum"), Volume=("Quantity", "sum"), Deals=("DEALS", "sum")
    ).reset_index()
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        f = px.bar(comp, x="Security Class", y="Turnover",
                   color="Security Class", color_discrete_map={"Equity Security": ACCENT, "Debt Security": PRIMARY},
                   title="Turnover")
        f.update_layout(yaxis_title="RWF", xaxis_title="")
        st.plotly_chart(f, use_container_width=True)
    with cc2:
        f = px.bar(comp, x="Security Class", y="Deals",
                   color="Security Class", color_discrete_map={"Equity Security": ACCENT, "Debt Security": PRIMARY},
                   title="Deals")
        f.update_layout(xaxis_title="")
        st.plotly_chart(f, use_container_width=True)
    with cc3:
        f = px.bar(comp, x="Security Class", y="Volume",
                   color="Security Class", color_discrete_map={"Equity Security": ACCENT, "Debt Security": PRIMARY},
                   title="Volume")
        f.update_layout(xaxis_title="")
        st.plotly_chart(f, use_container_width=True)
    st.caption("Debt Securities carry substantially higher face values per Deal than Equity Securities, so "
               "Deal count is the more comparable metric of relative market activity between security types.")

    st.markdown("### Top 10 Securities by Turnover")
    top10 = df.groupby("Security Name")["Turnover"].sum().nlargest(10).reset_index()
    fig5 = px.bar(top10.sort_values("Turnover"), x="Turnover", y="Security Name", orientation="h",
                  color_discrete_sequence=[ACCENT2])
    fig5.update_layout(xaxis_title="Turnover (RWF)", yaxis_title="")
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### Broker Activity — Buyer Code vs. Seller Code Turnover")
    buy = df.groupby("Buyer Code")["Turnover"].sum().rename("Buyer Code Turnover")
    sell = df.groupby("Seller Code")["Turnover"].sum().rename("Seller Code Turnover")
    broker_cmp = pd.concat([buy, sell], axis=1).fillna(0).reset_index().rename(columns={"index": "Broker Code"})
    broker_cmp_melt = broker_cmp.melt(id_vars="Broker Code", var_name="Side", value_name="Turnover")
    fig6 = px.bar(broker_cmp_melt, x="Broker Code", y="Turnover", color="Side", barmode="group",
                  color_discrete_map={"Buyer Code Turnover": ACCENT, "Seller Code Turnover": PRIMARY})
    fig6.update_layout(yaxis_title="Turnover (RWF)")
    st.plotly_chart(fig6, use_container_width=True)
    st.caption("Turnover attributed to each Broker Code, split by side of the transaction (Buyer Code vs. Seller Code).")

# ============================================================================
# TAB 4 — DISTRIBUTIONS
# ============================================================================
with tabs[3]:
    st.markdown("### Deal Frequency by Day of Week")
    dow = df.copy()
    dow["Day of Week"] = dow["Posting Date"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_counts = dow.groupby("Day of Week")["DEALS"].sum().reindex(order).dropna().reset_index()
    fig_dow = px.bar(dow_counts, x="Day of Week", y="DEALS", color_discrete_sequence=[ACCENT])
    fig_dow.update_layout(yaxis_title="Deals", xaxis_title="")
    st.plotly_chart(fig_dow, use_container_width=True)
    st.caption("Aggregate Deal count by weekday — a quick read on the trading calendar's busiest sessions.")

    st.markdown("### Price Dispersion by Security (Equity Securities)")
    eq = df[df["Asset Type"] == "Equity"]
    if not eq.empty:
        fig8 = px.box(eq, x="Security Name", y="Price", color="Security Name")
        fig8.update_layout(showlegend=False, xaxis_title="", yaxis_title="Price")
        st.plotly_chart(fig8, use_container_width=True)
        st.caption("Interquartile Price range per Equity Security — a wider box indicates greater intra-month "
                   "Price dispersion.")
    else:
        st.info("No Equity Securities in the current filter selection.")

    st.markdown("### Deal Count by Security")
    deals_sec = df.groupby("Security Name")["DEALS"].sum().sort_values(ascending=False).reset_index()
    fig9 = px.bar(deals_sec, x="Security Name", y="DEALS", color_discrete_sequence=[ACCENT2])
    fig9.update_layout(xaxis_tickangle=-45, xaxis_title="", yaxis_title="Deals")
    st.plotly_chart(fig9, use_container_width=True)

# ============================================================================
# TAB 5 — ALERTS
# ============================================================================
with tabs[4]:
    st.markdown("### Flags Requiring Review")

    st.markdown(f"""<div class="alert-box alert-warn">
    <b>Data quality note:</b> the source file included one aggregate summary row and two mistyped Broker Codes
    (<code>B10</code> and <code>BRK10</code>, both corrected to <code>BR10</code>). These were normalized prior
    to analysis.
    </div>""", unsafe_allow_html=True)

    # Broker concentration
    broker_turnover = pd.concat([
        df.groupby("Buyer Code")["Turnover"].sum(),
        df.groupby("Seller Code")["Turnover"].sum()
    ]).groupby(level=0).sum().sort_values(ascending=False)
    top_share = broker_turnover.iloc[0] / broker_turnover.sum() * 100
    if top_share > 40:
        st.markdown(f"""<div class="alert-box alert-danger"><b>High counterparty concentration:</b>
        Broker Code <b>{broker_turnover.index[0]}</b> accounts for <b>{top_share:.1f}%</b> of Turnover in the
        current selection, above the 40% concentration watch threshold.</div>""", unsafe_allow_html=True)
    elif top_share > 25:
        st.markdown(f"""<div class="alert-box alert-warn"><b>Moderate counterparty concentration:</b>
        Broker Code <b>{broker_turnover.index[0]}</b> accounts for <b>{top_share:.1f}%</b> of Turnover.</div>""",
        unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="alert-box alert-good"><b>Diversified counterparty base:</b>
        no single Broker Code exceeds 25% of Turnover (leading Broker Code: {top_share:.1f}%).</div>""",
        unsafe_allow_html=True)

    # Block trades
    thresh = df["Turnover"].quantile(0.95)
    large_trades = df[df["Turnover"] >= thresh].sort_values("Turnover", ascending=False)
    st.markdown(f"""<div class="alert-box alert-warn"><b>{len(large_trades)} block trades flagged</b>
    (top 5th percentile of Turnover, ≥ RWF {thresh:,.0f}) — predominantly Debt Securities, consistent with
    typical bond face values. Reviewed below.</div>""", unsafe_allow_html=True)
    st.dataframe(large_trades[["Posting Date","Security Name","Asset Type","Buyer Code","Seller Code","Quantity","Price","Turnover"]],
                 use_container_width=True, hide_index=True)

    # Illiquid securities
    low_liquidity = df.groupby("Security Name")["DEALS"].sum().sort_values()
    low_liquidity = low_liquidity[low_liquidity <= 1]
    if len(low_liquidity) > 0:
        st.markdown(f"""<div class="alert-box alert-warn"><b>Thin liquidity watch:</b>
        {len(low_liquidity)} securities recorded a single Deal in this period: {', '.join(low_liquidity.index[:10])}
        {'...' if len(low_liquidity) > 10 else ''}</div>""", unsafe_allow_html=True)

# ============================================================================
# TAB 6 — DATA EXPLORER
# ============================================================================
with tabs[5]:
    st.markdown("### Explore the Filtered Dataset")
    search = st.text_input("Search (Security, Security Name, or Broker Code)", "")
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
        view[["Posting Date","Security","Security Name","Asset Type","Buyer Code","Seller Code","Quantity","Price","Turnover","DEALS"]],
        use_container_width=True, hide_index=True
    )
    st.caption(f"Showing {len(view)} of {len(df)} filtered deals.")

    csv = view.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download this table as CSV", data=csv, file_name="rse_filtered_trades.csv", mime="text/csv")

# ============================================================================
# TAB 7 — ETHICS & INSIGHTS
# ============================================================================
with tabs[6]:
    st.markdown("### Market Concentration Analysis")
    shares = (broker_turnover / broker_turnover.sum())
    hhi = (shares ** 2).sum() * 10000
    st.metric("Herfindahl-Hirschman Index (HHI) — Broker Codes, by Turnover", f"{hhi:,.0f}")
    if hhi > 2500:
        level, tone = "Highly concentrated", "alert-danger"
    elif hhi > 1500:
        level, tone = "Moderately concentrated", "alert-warn"
    else:
        level, tone = "Competitive / unconcentrated", "alert-good"
    st.markdown(f"""<div class="alert-box {tone}"><b>{level}</b> market structure per standard HHI thresholds
    (U.S. DOJ/FTC guidelines: &lt;1,500 unconcentrated, 1,500–2,500 moderate, &gt;2,500 high). Leading Broker
    Code <b>{broker_turnover.index[0]}</b> holds a {top_share:.1f}% Turnover share.</div>""",
    unsafe_allow_html=True)

    st.markdown("### Fairness & Transparency Notes")
    st.markdown("""
- **Counterparty anonymity.** Buyer Code and Seller Code identify brokers, not the underlying firms — appropriate
  for public disclosure but limiting for accountability analysis without a code-to-firm mapping.
- **Liquidity access.** Several securities recorded only a single Deal this month. Thin liquidity widens the
  effective bid-ask spread and makes single-Deal Prices a less reliable proxy for fair value.
- **Data completeness.** This dataset spans one Posting Date range only; concentration and liquidity findings
  should be validated against a longer time series before being treated as structural.
- **Cross-asset comparability.** Because Turnover on Debt Securities reflects face value, blending Equity and
  Debt Turnover in a single ranking can overstate the relative importance of the bond market — Deal count is
  the fairer cross-asset comparison.
    """)

    st.markdown("### Key Insights")
    n_rare = df.groupby("Security Name")["DEALS"].sum().le(1).sum()
    insights = [
        f"**{top_ticker} ({top_security})** led Turnover for the period, alongside significant activity in longer-dated Debt Securities.",
        f"Counterparty participation is {'uneven' if hhi > 1500 else 'reasonably balanced'} (HHI = {hhi:,.0f}).",
        f"{n_rare} securities recorded a single Deal, indicating a long tail of illiquid instruments alongside a small set of actively traded names.",
        "Block trades in Debt Securities are the principal driver of extreme Turnover values and should be benchmarked separately from Equity Securities.",
    ]
    for i in insights:
        st.markdown(f"- {i}")

# ============================================================================
# TAB 8 — GLOSSARY
# ============================================================================
with tabs[7]:
    st.markdown("### Glossary of Technical Terms")
    st.markdown("<p class='section-note'>Definitions of the dataset variables and market terminology used throughout this dashboard.</p>", unsafe_allow_html=True)

    glossary = [
        ("Security", "A tradable financial instrument listed on the Exchange — either an Equity Security (a listed company's shares) or a Debt Security (a bond). Identified in the dataset by its ticker (the <b>Security</b> column) and full issuer name (<b>Security Name</b>)."),
        ("Equity Security", "A Security representing ownership in a listed company (e.g. Bank of Kigali, Bralirwa). Holders are entitled to dividends and residual claims on the company."),
        ("Debt Security (Bond)", "A Security representing a loan from the investor to the issuer (government or corporate), repaid with interest. Bond Quantity typically reflects a much larger face value than an equivalent Equity Quantity."),
        ("Posting Date", "The date a Deal was recorded/settled on the Exchange's trading system."),
        ("Buyer Code / Seller Code", "The broker identifier for the buy-side and sell-side counterparties in a Deal. Used to assess broker-level trading activity and counterparty concentration."),
        ("Quantity", "The number of units (shares or bond units) exchanged in a Deal."),
        ("Price", "The per-unit transaction price for a Deal, expressed in RWF."),
        ("Turnover", "The total monetary value of a Deal, calculated as Price × Quantity. Aggregate Turnover is the standard measure of market activity by value."),
        ("Deals", "The count of individual executed transactions. Deal count is the standard measure of market activity by frequency, and is more comparable across Equity and Debt Securities than Turnover."),
        ("Volume", "The aggregate Quantity of units traded across one or more Deals."),
        ("Block Trade", "An unusually large single Deal (in this dashboard, defined as Turnover in the top 5th percentile) — common for Debt Securities given their higher face values."),
        ("Liquidity", "The ease with which a Security can be bought or sold without materially moving its Price. Securities with very few Deals in a period are considered thinly traded (illiquid)."),
        ("Market Concentration", "The degree to which trading activity is dominated by a small number of participants (here, Broker Codes)."),
        ("Herfindahl-Hirschman Index (HHI)", "A standard concentration measure calculated as the sum of squared market shares (×10,000). Values below 1,500 indicate an unconcentrated market, 1,500–2,500 a moderately concentrated market, and above 2,500 a highly concentrated market, per U.S. DOJ/FTC guidelines."),
        ("Counterparty", "The opposing party (broker) to a trade — i.e., the Buyer Code relative to the Seller Code, or vice versa."),
    ]
    for term, definition in glossary:
        st.markdown(f"""<div class="glossary-term"><b>{term}</b><br>{definition}</div>""", unsafe_allow_html=True)

# ============================================================================
# TAB 9 — RECOMMENDATIONS
# ============================================================================
with tabs[8]:
    st.markdown("### Recommendations")
    st.markdown(f"""
1. **Monitor counterparty concentration.** With an HHI of {hhi:,.0f}, continue tracking whether Turnover
   broadens across more Broker Codes or continues concentrating among a small set of counterparties.
2. **Report Equity and Debt Securities separately.** Because bond face values distort blended Turnover
   figures, disclose Equity and Debt Turnover on separate scales (or by Deal count) in executive reporting.
3. **Review block trades individually.** The top 5th percentile of Deals by Turnover disproportionately
   shapes monthly aggregates; a manual review each period would catch data errors early and surface genuine
   market-moving events.
4. **Address thin liquidity.** Securities with a single Deal per period may warrant liquidity-support measures
   (e.g., market-maker incentives) or targeted investor outreach.
5. **Strengthen data entry controls.** The two Broker Code typos identified this period suggest a validated
   lookup (rather than free-text entry) at the point of trade capture would reduce downstream cleanup.
6. **Extend the time series.** A single Posting Date range limits trend inference — ingesting additional
   months would enable genuine month-over-month and seasonal analysis of Turnover, Deals, and Volume.
    """)
    st.info("💡 Tip: use the sidebar filters to re-run this entire dashboard — including the Market "
            "Commentary and HHI — on any Posting Date range, Security Type, Security, or Broker Code.")
