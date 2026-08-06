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
# THEME / CSS — RSE brand palette: mainly green, with dark blue and yellow accents
# ----------------------------------------------------------------------------
PRIMARY = "#0F7B42"      # RSE green (main brand color)
SECONDARY = "#0B2545"    # dark blue (secondary accent)
ACCENT2 = "#E8B923"      # yellow (small accents only)
DANGER = "#C1121F"
WARN = "#B9770E"
GOOD = "#1E8449"

# Mostly greens, with dark blue and yellow used sparingly, as on the RSE brand
COLOR_SEQUENCE = ["#0F7B42", "#0B2545", "#E8B923", "#4CAF50", "#1B5E20",
                   "#154360", "#79C68F", "#F2C94C"]

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
    .kpi-label {{ font-size: 13px; color: #D6ECDE; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 26px; font-weight: 700; color: #FFFFFF; }}
    .kpi-sub {{ font-size: 12px; color: #B9DCC5; }}
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
        background: linear-gradient(135deg, {PRIMARY} 0%, #0B4D2A 100%);
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
    .definition-box .source {{ font-size: 13px; color: #D6ECDE; font-style: normal; text-align: right; }}
    .glossary-term {{
        background-color: #F2F8F4; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;
        border-left: 4px solid {SECONDARY};
        color: #1A1A2E;
    }}
    .glossary-term b {{ color: {PRIMARY}; }}
    .stTabs [data-baseweb="tab"] {{ color: {SECONDARY}; }}
</style>
""", unsafe_allow_html=True)

px.defaults.color_discrete_sequence = COLOR_SEQUENCE
px.defaults.template = "plotly_white"
GREEN_SCALE = ["#FBEFC0", "#E8B923", "#79C68F", "#1E8449", "#0B4D2A"]

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
<p>The Rwanda Stock Exchange is the national securities exchange of Rwanda, providing a regulated marketplace
for buying, selling, and listing financial instruments such as shares, corporate bonds, and government
securities. It is an organized and regulated financial market where securities are bought and sold at prices
governed by the forces of demand and supply.</p>
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
    "🔗 Variations & Correlations", "🚨 Alerts", "🔍 Data Explorer",
    "🧭 Ethics & Insights", "📖 Glossary", "✅ Recommendations"
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
                 color="Security Class", color_discrete_map={"Equity Security": SECONDARY, "Debt Security": PRIMARY})
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
    fig2 = px.bar(daily, x="Posting Date", y="Deals", color_discrete_sequence=[SECONDARY])
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
                  color_discrete_map={"Equity Security": SECONDARY, "Debt Security": PRIMARY})
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
                   color="Security Class", color_discrete_map={"Equity Security": SECONDARY, "Debt Security": PRIMARY},
                   title="Turnover")
        f.update_layout(yaxis_title="RWF", xaxis_title="")
        st.plotly_chart(f, use_container_width=True)
    with cc2:
        f = px.bar(comp, x="Security Class", y="Deals",
                   color="Security Class", color_discrete_map={"Equity Security": SECONDARY, "Debt Security": PRIMARY},
                   title="Deals")
        f.update_layout(xaxis_title="")
        st.plotly_chart(f, use_container_width=True)
    with cc3:
        f = px.bar(comp, x="Security Class", y="Volume",
                   color="Security Class", color_discrete_map={"Equity Security": SECONDARY, "Debt Security": PRIMARY},
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
                  color_discrete_map={"Buyer Code Turnover": PRIMARY, "Seller Code Turnover": SECONDARY})
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
    fig_dow = px.bar(dow_counts, x="Day of Week", y="DEALS", color_discrete_sequence=[PRIMARY])
    fig_dow.update_layout(yaxis_title="Deals", xaxis_title="")
    st.plotly_chart(fig_dow, use_container_width=True)
    st.caption("Aggregate Deal count by weekday — a quick read on the trading calendar's busiest sessions.")

    st.markdown("### Price Dispersion by Security (Equity Securities)")
    eq = df[df["Asset Type"] == "Equity"]
    if not eq.empty:
        fig8 = px.box(eq, x="Security Name", y="Price", color="Security Name",
                      color_discrete_sequence=COLOR_SEQUENCE)
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
# TAB 5 — VARIATIONS & CORRELATIONS
# ============================================================================
with tabs[4]:
    st.markdown("### Price Variation by Security (Equity Securities)")
    st.markdown("<p class='section-note'>The Coefficient of Variation (CV) expresses Price variability "
                "relative to the average Price, so securities at very different Price levels can be compared "
                "fairly. A higher CV means the Price moved around more during the month, relative to its own "
                "average — in plain terms, a more volatile trading Price.</p>", unsafe_allow_html=True)
    if not eq.empty:
        var_stats = eq.groupby("Security Name")["Price"].agg(["mean", "std", "count"]).fillna(0)
        var_stats["CV (%)"] = np.where(var_stats["mean"] > 0, (var_stats["std"] / var_stats["mean"]) * 100, 0)
        var_stats = var_stats.sort_values("CV (%)", ascending=False).reset_index()
        fig_cv = px.bar(var_stats, x="Security Name", y="CV (%)", color_discrete_sequence=[PRIMARY])
        fig_cv.update_layout(xaxis_title="", yaxis_title="Coefficient of Variation (%)", xaxis_tickangle=-45)
        st.plotly_chart(fig_cv, use_container_width=True)
        most_variable = var_stats.iloc[0]["Security Name"] if len(var_stats) else "N/A"
        st.caption(f"**{most_variable}** shows the highest Price variability relative to its average Price "
                   f"in the current selection.")
    else:
        st.info("No Equity Securities in the current filter selection.")

    st.markdown("### Correlation Matrix — Quantity, Price, Turnover, Deals")
    st.markdown("<p class='section-note'>The Correlation Coefficient measures how strongly two variables move "
                "together, on a scale from -1 to +1. A value near +1 means they rise and fall together "
                "(a strong positive relationship); near -1 means one rises as the other falls (a strong "
                "negative relationship); near 0 means little to no straight-line relationship between them.</p>",
                unsafe_allow_html=True)
    num_cols = ["Quantity", "Price", "Turnover", "DEALS"]
    corr = df[num_cols].corr().round(2)
    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale=GREEN_SCALE,
                          zmin=-1, zmax=1, aspect="auto")
    fig_corr.update_layout(coloraxis_colorbar=dict(title="Correlation"))
    st.plotly_chart(fig_corr, use_container_width=True)

    tq_corr = corr.loc["Turnover", "Quantity"]
    tp_corr = corr.loc["Turnover", "Price"]
    qd_corr = corr.loc["Quantity", "DEALS"]

    def describe_corr(value):
        strength = "strong" if abs(value) >= 0.7 else "moderate" if abs(value) >= 0.4 else "weak"
        direction = "positive" if value >= 0 else "negative"
        return f"{strength} {direction}"

    st.markdown(f"""
- **Turnover and Quantity: {tq_corr:.2f}** — a {describe_corr(tq_corr)} relationship. This is expected,
  since Turnover is calculated directly from Price × Quantity, so Deals with larger Quantity tend to carry
  higher Turnover.
- **Turnover and Price: {tp_corr:.2f}** — a {describe_corr(tp_corr)} relationship, showing how much Turnover
  is driven by the per-unit Price rather than the number of units traded.
- **Quantity and Deals: {qd_corr:.2f}** — a {describe_corr(qd_corr)} relationship between how many units
  change hands and how many separate transactions it takes to move them.
    """)

    st.markdown("### Turnover vs. Quantity — Relationship by Security Type")
    fig_sc1 = px.scatter(df, x="Quantity", y="Turnover", color="Security Class", trendline="ols",
                         color_discrete_map={"Equity Security": SECONDARY, "Debt Security": PRIMARY},
                         hover_data=["Security Name", "Price", "Posting Date"])
    fig_sc1.update_layout(xaxis_title="Quantity (units)", yaxis_title="Turnover (RWF)")
    st.plotly_chart(fig_sc1, use_container_width=True)
    st.caption("Each point is one Deal. The trend line shows the general direction of the relationship "
               "between Quantity and Turnover for each Security Type.")

    st.markdown("### Price vs. Deal Count — Relationship (Equity Securities)")
    if not eq.empty:
        eq_deals = eq.groupby("Security Name").agg(
            Avg_Price=("Price", "mean"), Total_Deals=("DEALS", "sum")
        ).reset_index()
        fig_sc2 = px.scatter(eq_deals, x="Avg_Price", y="Total_Deals", text="Security Name",
                             color_discrete_sequence=[PRIMARY], trendline="ols")
        fig_sc2.update_traces(textposition="top center")
        fig_sc2.update_layout(xaxis_title="Average Price (RWF)", yaxis_title="Total Deals")
        st.plotly_chart(fig_sc2, use_container_width=True)
        st.caption("Tests whether higher-priced Equity Securities trade less often than lower-priced ones — "
                   "a weak or flat trend line means Price level alone does not strongly explain trading "
                   "frequency in this selection.")
    else:
        st.info("No Equity Securities in the current filter selection.")

# ============================================================================
# TAB 6 — ALERTS
# ============================================================================
with tabs[5]:
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
        current selection, above the 40% concentration watch threshold. <i>In plain terms: one broker is
        responsible for most of the buying and selling — if that broker slowed down, overall market activity
        would drop sharply.</i></div>""", unsafe_allow_html=True)
    elif top_share > 25:
        st.markdown(f"""<div class="alert-box alert-warn"><b>Moderate counterparty concentration:</b>
        Broker Code <b>{broker_turnover.index[0]}</b> accounts for <b>{top_share:.1f}%</b> of Turnover.
        <i>In plain terms: one broker is more active than the rest, but the market doesn't depend on them
        alone.</i></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="alert-box alert-good"><b>Diversified counterparty base:</b>
        no single Broker Code exceeds 25% of Turnover (leading Broker Code: {top_share:.1f}%).
        <i>In plain terms: trading activity is shared fairly evenly across brokers — a healthy sign.</i></div>""",
        unsafe_allow_html=True)

    # Block trades
    thresh = df["Turnover"].quantile(0.95)
    large_trades = df[df["Turnover"] >= thresh].sort_values("Turnover", ascending=False)
    st.markdown(f"""<div class="alert-box alert-warn"><b>{len(large_trades)} block trades flagged</b>
    (top 5th percentile of Turnover, ≥ RWF {thresh:,.0f}) — predominantly Debt Securities, consistent with
    typical bond face values. <i>In plain terms: these are the biggest single trades of the month. Most are
    normal, large bond deals — but each is worth a quick look to rule out data entry errors.</i></div>""",
    unsafe_allow_html=True)
    st.dataframe(large_trades[["Posting Date","Security Name","Asset Type","Buyer Code","Seller Code","Quantity","Price","Turnover"]],
                 use_container_width=True, hide_index=True)

    # Illiquid securities
    low_liquidity = df.groupby("Security Name")["DEALS"].sum().sort_values()
    low_liquidity = low_liquidity[low_liquidity <= 1]
    if len(low_liquidity) > 0:
        st.markdown(f"""<div class="alert-box alert-warn"><b>Thin liquidity watch:</b>
        {len(low_liquidity)} securities recorded a single Deal in this period: {', '.join(low_liquidity.index[:10])}
        {'...' if len(low_liquidity) > 10 else ''}. <i>In plain terms: these securities barely traded at all,
        so it could be harder to buy or sell them quickly at a fair price.</i></div>""", unsafe_allow_html=True)

# ============================================================================
# TAB 7 — DATA EXPLORER
# ============================================================================
with tabs[6]:
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
# TAB 8 — ETHICS & INSIGHTS
# ============================================================================
with tabs[7]:
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
    Code <b>{broker_turnover.index[0]}</b> holds a {top_share:.1f}% Turnover share. <i>In plain terms: the HHI
    is a standard way to measure how spread out trading is among brokers — a low number means many brokers
    share the activity, a high number means a few brokers dominate it.</i></div>""",
    unsafe_allow_html=True)

    st.markdown("### Fairness & Transparency Notes")
    st.markdown("""
- **Counterparty anonymity.** Buyer Code and Seller Code identify brokers, not the underlying firms — appropriate
  for public disclosure but limiting for accountability analysis without a code-to-firm mapping. *In plain terms:
  we can see which broker made a trade, but not which client or company was behind it.*
- **Liquidity access.** Several securities recorded only a single Deal this month. Thin liquidity widens the
  effective bid-ask spread and makes single-Deal Prices a less reliable proxy for fair value. *In plain terms:
  a security that barely trades is harder to buy or sell quickly, and its last recorded price may not reflect
  what it's really worth today.*
- **Data completeness.** This dataset spans one Posting Date range only; concentration and liquidity findings
  should be validated against a longer time series before being treated as structural. *In plain terms: one
  month of data isn't enough to call something a long-term pattern — it needs to be checked against future
  months.*
- **Cross-asset comparability.** Because Turnover on Debt Securities reflects face value, blending Equity and
  Debt Turnover in a single ranking can overstate the relative importance of the bond market — Deal count is
  the fairer cross-asset comparison. *In plain terms: comparing shares and bonds by money value alone is
  misleading, since bonds are naturally traded in bigger amounts.*
    """)

    st.markdown("### Key Insights")
    n_rare = df.groupby("Security Name")["DEALS"].sum().le(1).sum()
    insights = [
        f"**{top_ticker} ({top_security})** led Turnover for the period, alongside significant activity in longer-dated Debt Securities — meaning it had the highest total money value traded of any security this month.",
        f"Counterparty participation is {'uneven' if hhi > 1500 else 'reasonably balanced'} (HHI = {hhi:,.0f}) — {'one or two brokers handle most of the activity' if hhi > 1500 else 'trading is spread across a healthy number of brokers'}.",
        f"{n_rare} securities recorded a single Deal, indicating a long tail of illiquid instruments alongside a small set of actively traded names — in other words, most trading is concentrated in just a handful of securities.",
        "Block trades in Debt Securities are the principal driver of extreme Turnover values and should be benchmarked separately from Equity Securities — a few very large bond trades can make the overall numbers look bigger than typical daily activity.",
        f"Turnover and Quantity show a **{describe_corr(tq_corr)}** relationship ({tq_corr:.2f}), confirming that Deal value is driven mainly by how many units are traded rather than Price alone in this selection.",
    ]
    for i in insights:
        st.markdown(f"- {i}")

# ============================================================================
# TAB 9 — GLOSSARY
# ============================================================================
with tabs[8]:
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
        ("Variance / Standard Deviation", "Standard statistical measures of how spread out a set of values is around its average. Standard Deviation is the square root of Variance and is expressed in the same unit as the original data (e.g. RWF for Price)."),
        ("Coefficient of Variation (CV)", "Standard Deviation divided by the mean, usually shown as a percentage. It measures relative variability, allowing fair comparison of Price volatility between securities that trade at very different Price levels."),
        ("Correlation Coefficient", "A statistic from -1 to +1 that measures how strongly two numeric variables move together. +1 means they move perfectly together, -1 means they move perfectly opposite, and 0 means no straight-line relationship."),
        ("Trend Line (OLS)", "A straight line fitted through a scatter of data points (using Ordinary Least Squares) to show the general direction of the relationship between two variables."),
    ]
    for term, definition in glossary:
        st.markdown(f"""<div class="glossary-term"><b>{term}</b><br>{definition}</div>""", unsafe_allow_html=True)

# ============================================================================
# TAB 10 — RECOMMENDATIONS
# ============================================================================
with tabs[9]:
    st.markdown("### Recommendations")
    st.markdown(f"""
1. **Monitor counterparty concentration.** With an HHI of {hhi:,.0f}, continue tracking whether Turnover
   broadens across more Broker Codes or continues concentrating among a small set of counterparties.
   *Simply put: keep an eye on whether trading stays spread across many brokers or leans on just one or two.*
2. **Report Equity and Debt Securities separately.** Because bond face values distort blended Turnover
   figures, disclose Equity and Debt Turnover on separate scales (or by Deal count) in executive reporting.
   *Simply put: don't lump shares and bonds together in the same total — it makes bonds look more important
   than they really are.*
3. **Review block trades individually.** The top 5th percentile of Deals by Turnover disproportionately
   shapes monthly aggregates; a manual review each period would catch data errors early and surface genuine
   market-moving events. *Simply put: double-check the handful of biggest trades each month — most are fine,
   but it's the fastest way to catch mistakes or spot something important.*
4. **Address thin liquidity.** Securities with a single Deal per period may warrant liquidity-support measures
   (e.g., market-maker incentives) or targeted investor outreach. *Simply put: securities that rarely trade
   may need extra support or promotion to attract more buyers and sellers.*
5. **Strengthen data entry controls.** The two Broker Code typos identified this period suggest a validated
   lookup (rather than free-text entry) at the point of trade capture would reduce downstream cleanup.
   *Simply put: use a dropdown list instead of free typing for broker codes to avoid simple mistakes.*
6. **Extend the time series.** A single Posting Date range limits trend inference — ingesting additional
   months would enable genuine month-over-month and seasonal analysis of Turnover, Deals, and Volume.
   *Simply put: one month isn't enough to spot real trends — adding more months will show the bigger picture.*
7. **Use the Correlation and Variation findings to guide monitoring.** Since Turnover is driven mainly by
   Quantity ({tq_corr:.2f} correlation), focus surveillance on unusually large Quantity trades rather than
   Price spikes alone. *Simply put: watch for big trade sizes, not just big prices, when checking for unusual
   activity.*
    """)
    st.info("💡 Tip: use the sidebar filters to re-run this entire dashboard — including the Market "
            "Commentary, HHI, and Correlation figures — on any Posting Date range, Security Type, Security, "
            "or Broker Code.")
