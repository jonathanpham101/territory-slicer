import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Territory Slicer", page_icon="🎯", layout="wide")

# =====================================================
# CUSTOM CSS — Polished dark dashboard
# =====================================================
st.markdown("""
<style>
    /* --- Global --- */
    .stApp {
        background-color: #09090b;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background: #09090b;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }
    .sidebar-brand {
        text-align: center;
        padding: 1.5rem 0 1.25rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 1.5rem;
    }
    .sidebar-brand h1 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .sidebar-brand p {
        font-size: 0.65rem;
        color: #52525b;
        margin: 0.4rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 500;
    }
    .sidebar-stat {
        display: inline-block;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.3rem 0.7rem;
        margin: 0.15rem 0.1rem;
        font-size: 0.78rem;
        color: #a1a1aa;
    }

    /* --- Metric cards --- */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1.4rem 1.2rem;
        transition: border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(255, 255, 255, 0.15);
    }
    div[data-testid="stMetric"] label {
        color: #71717a !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.6rem !important;
    }

    /* --- Section headers --- */
    .section-header {
        border-left: 3px solid;
        padding-left: 14px;
        margin: 3rem 0 1.5rem 0;
    }
    .section-header h2 {
        font-size: 1.2rem;
        font-weight: 600;
        color: #fafafa;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .section-header p {
        font-size: 0.8rem;
        color: #52525b;
        margin: 0.3rem 0 0 0;
        font-weight: 400;
    }

    /* --- Spacer --- */
    .spacer { margin-top: 1.5rem; }
    .spacer-lg { margin-top: 2.5rem; }

    /* --- Dividers --- */
    hr {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin: 3rem 0;
    }

    /* --- DataFrames --- */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        overflow: hidden;
    }

    /* --- Download button --- */
    .stDownloadButton button {
        background: #fafafa !important;
        color: #09090b !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.55rem 1.6rem !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
    }

    /* --- Slider polish --- */
    .stSlider [data-testid="stTickBar"] {
        display: none;
    }

    /* --- Caption styling --- */
    .stCaption {
        color: #52525b !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# PLOTLY THEME
# =====================================================
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#a1a1aa", size=11, family="Inter, system-ui, sans-serif"),
    title_font=dict(color="#d4d4d8", size=13, family="Inter, system-ui, sans-serif"),
    hoverlabel=dict(bgcolor="#18181b", font_color="#fafafa", bordercolor="#27272a"),
)
CHART_GRID = dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.06)")

# Color palette
ENTERPRISE_COLOR = "#4F8FF7"
MIDMARKET_COLOR = "#34D399"
ACCENT_ORANGE = "#FB923C"
ACCENT_PURPLE = "#A78BFA"

# Required columns
REPS_REQUIRED_COLS = {"Rep_Name", "Location", "Segment"}
ACCOUNTS_REQUIRED_COLS = {
    "Account_ID", "Account_Name", "Current_Rep", "ARR",
    "Location", "Num_Employees", "Num_Marketers", "Risk_Score",
}

# =====================================================
# DATA LOADING
# =====================================================
@st.cache_data
def load_sample_data():
    reps = pd.read_excel("GTM-Engineer Challenge.xlsx", sheet_name="Reps")
    accounts = pd.read_excel("GTM-Engineer Challenge.xlsx", sheet_name="Accounts")
    return reps, accounts

def validate_columns(df: pd.DataFrame, required: set, label: str) -> list[str]:
    """Return list of missing columns, empty if all present."""
    return sorted(required - set(df.columns))

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h1>🎯 Territory Slicer</h1>
        <p>Dynamic Assignment Engine</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Data Source ---
    data_source = st.radio("Data Source", ["Use Sample Data", "Upload Your Own"], index=0)

    reps_df = None
    accounts_df = None

    if data_source == "Use Sample Data":
        reps_df, accounts_df = load_sample_data()
    else:
        st.caption("Upload an Excel file with 'Reps' and 'Accounts' sheets, or two separate CSV files.")
        file_format = st.radio("File format", ["Excel (.xlsx)", "CSV (two files)"], index=0,
                               label_visibility="collapsed")

        if file_format == "Excel (.xlsx)":
            uploaded = st.file_uploader("Upload Excel file", type=["xlsx"], label_visibility="collapsed")
            if uploaded is not None:
                try:
                    reps_df = pd.read_excel(uploaded, sheet_name="Reps")
                    accounts_df = pd.read_excel(uploaded, sheet_name="Accounts")
                except Exception as e:
                    st.error(f"Could not read sheets: {e}")
                    st.info("Make sure your file has sheets named 'Reps' and 'Accounts'.")
        else:
            reps_file = st.file_uploader("Upload Reps CSV", type=["csv"])
            accounts_file = st.file_uploader("Upload Accounts CSV", type=["csv"])
            if reps_file is not None:
                reps_df = pd.read_csv(reps_file)
            if accounts_file is not None:
                accounts_df = pd.read_csv(accounts_file)

        # Validate uploaded data
        if reps_df is not None:
            missing = validate_columns(reps_df, REPS_REQUIRED_COLS, "Reps")
            if missing:
                st.error(f"Reps data missing columns: **{', '.join(missing)}**")
                reps_df = None

        if accounts_df is not None:
            missing = validate_columns(accounts_df, ACCOUNTS_REQUIRED_COLS, "Accounts")
            if missing:
                st.error(f"Accounts data missing columns: **{', '.join(missing)}**")
                accounts_df = None

    # Check if we have data to proceed
    data_ready = reps_df is not None and accounts_df is not None

    if data_ready:
        st.markdown("---")
        st.markdown(
            f'<div style="text-align:center; margin-bottom:0.5rem;">'
            f'<span class="sidebar-stat">{len(reps_df)} Reps</span>'
            f'<span class="sidebar-stat">{len(accounts_df)} Accounts</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        threshold = st.slider(
            "Employee Count Threshold",
            min_value=1_000,
            max_value=200_000,
            value=50_000,
            step=1_000,
            help="Accounts with employees >= this value → Enterprise.",
        )

        enterprise_mask = accounts_df["Num_Employees"] >= threshold
        enterprise_count = enterprise_mask.sum()
        midmarket_count = (~enterprise_mask).sum()

        st.markdown(
            f'<div style="margin-top:0.75rem;">'
            f'<span class="sidebar-stat">🏢 Enterprise: {enterprise_count}</span>'
            f'<span class="sidebar-stat">🏬 Mid-Market: {midmarket_count}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        STRATEGIES = {
            "ARR Balanced": "Equalizes total ARR across reps within each segment.",
            "ARR + Risk Balanced": "Balances ARR and distributes risk scores evenly across reps.",
            "ARR + Risk + Geography": "Balances ARR and risk, with affinity for reps in the same state.",
        }

        strategy = st.radio("Assignment Strategy", list(STRATEGIES.keys()), index=0)
        st.caption(STRATEGIES[strategy])

# =====================================================
# EARLY EXIT IF NO DATA
# =====================================================
if not data_ready:
    st.markdown("<br>" * 3, unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center; padding:4rem 2rem;">'
        '<p style="font-size:2.5rem; margin-bottom:0.5rem;">📁</p>'
        '<h2 style="color:#fafafa; font-weight:600; margin-bottom:0.5rem;">Upload your data to get started</h2>'
        '<p style="color:#52525b; font-size:0.9rem;">Select "Upload Your Own" in the sidebar and provide your Reps and Accounts data.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# =====================================================
# SEGMENTATION
# =====================================================
accounts_df["Assigned_Segment"] = accounts_df["Num_Employees"].apply(
    lambda x: "Enterprise" if x >= threshold else "Mid-Market"
)

enterprise_df = accounts_df[accounts_df["Assigned_Segment"] == "Enterprise"]
midmarket_df = accounts_df[accounts_df["Assigned_Segment"] == "Mid-Market"]

# =====================================================
# ASSIGNMENT ENGINE
# =====================================================

# Build rep location lookup from the Reps sheet
rep_location_map = dict(zip(reps_df["Rep_Name"], reps_df["Location"]))

def assign_arr_balanced(accounts: pd.DataFrame, rep_names: list[str]) -> pd.DataFrame:
    """Greedy: assign each account to the rep with the lowest total ARR."""
    sorted_accounts = accounts.sort_values("ARR", ascending=False).copy()
    rep_totals = {rep: 0 for rep in rep_names}
    assignments = []
    for _, row in sorted_accounts.iterrows():
        min_rep = min(rep_totals, key=rep_totals.get)
        assignments.append(min_rep)
        rep_totals[min_rep] += row["ARR"]
    sorted_accounts["Assigned_Rep"] = assignments
    return sorted_accounts

def assign_arr_risk(accounts: pd.DataFrame, rep_names: list[str]) -> pd.DataFrame:
    """Greedy: balance ARR (60%) and avg risk score (40%)."""
    sorted_accounts = accounts.sort_values("ARR", ascending=False).copy()
    total_arr = accounts["ARR"].sum()
    ideal_arr = total_arr / len(rep_names) if len(rep_names) > 0 else 1

    rep_totals = {rep: 0.0 for rep in rep_names}
    rep_risk_sum = {rep: 0.0 for rep in rep_names}
    rep_count = {rep: 0 for rep in rep_names}
    assignments = []

    for _, row in sorted_accounts.iterrows():
        best_rep = None
        best_score = float("inf")
        for rep in rep_names:
            arr_component = (rep_totals[rep] / ideal_arr) * 0.6
            avg_risk = rep_risk_sum[rep] / rep_count[rep] if rep_count[rep] > 0 else 0
            risk_component = (avg_risk / 100) * 0.4
            score = arr_component + risk_component
            if score < best_score:
                best_score = score
                best_rep = rep
        assignments.append(best_rep)
        rep_totals[best_rep] += row["ARR"]
        rep_risk_sum[best_rep] += row["Risk_Score"]
        rep_count[best_rep] += 1

    sorted_accounts["Assigned_Rep"] = assignments
    return sorted_accounts

def assign_arr_risk_geo(accounts: pd.DataFrame, rep_names: list[str]) -> pd.DataFrame:
    """Greedy: balance ARR (60%) + risk (40%), with -0.15 geo affinity bonus."""
    sorted_accounts = accounts.sort_values("ARR", ascending=False).copy()
    total_arr = accounts["ARR"].sum()
    ideal_arr = total_arr / len(rep_names) if len(rep_names) > 0 else 1

    rep_totals = {rep: 0.0 for rep in rep_names}
    rep_risk_sum = {rep: 0.0 for rep in rep_names}
    rep_count = {rep: 0 for rep in rep_names}
    assignments = []

    for _, row in sorted_accounts.iterrows():
        best_rep = None
        best_score = float("inf")
        for rep in rep_names:
            arr_component = (rep_totals[rep] / ideal_arr) * 0.6
            avg_risk = rep_risk_sum[rep] / rep_count[rep] if rep_count[rep] > 0 else 0
            risk_component = (avg_risk / 100) * 0.4
            score = arr_component + risk_component
            # Geography bonus
            if rep_location_map.get(rep) == row["Location"]:
                score -= 0.15
            if score < best_score:
                best_score = score
                best_rep = rep
        assignments.append(best_rep)
        rep_totals[best_rep] += row["ARR"]
        rep_risk_sum[best_rep] += row["Risk_Score"]
        rep_count[best_rep] += 1

    sorted_accounts["Assigned_Rep"] = assignments
    return sorted_accounts

# Select assignment function based on strategy
STRATEGY_FN = {
    "ARR Balanced": assign_arr_balanced,
    "ARR + Risk Balanced": assign_arr_risk,
    "ARR + Risk + Geography": assign_arr_risk_geo,
}
assign_fn = STRATEGY_FN[strategy]

enterprise_reps = reps_df[reps_df["Segment"] == "Enterprise"]["Rep_Name"].tolist()
midmarket_reps = reps_df[reps_df["Segment"] == "Mid Market"]["Rep_Name"].tolist()

enterprise_assigned = assign_fn(enterprise_df, enterprise_reps)
midmarket_assigned = assign_fn(midmarket_df, midmarket_reps)

# =====================================================
# HELPERS
# =====================================================
def build_summary(assigned_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        assigned_df.groupby("Assigned_Rep")
        .agg(Accounts=("Account_ID", "count"), Total_ARR=("ARR", "sum"))
        .reset_index()
    )
    summary["Avg_ARR"] = summary["Total_ARR"] / summary["Accounts"]
    summary.columns = ["Rep Name", "# Accounts", "Total ARR", "Avg ARR per Account"]
    return summary.sort_values("Total ARR", ascending=False)

def build_arr_chart(summary: pd.DataFrame, color: str):
    sorted_df = summary.sort_values("Total ARR", ascending=True)
    fig = px.bar(sorted_df, x="Total ARR", y="Rep Name", orientation="h",
                 text="Total ARR", color_discrete_sequence=[color])
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="inside",
                      textfont=dict(color="white", size=11), marker_line_width=0,
                      marker_opacity=0.9)
    max_val = sorted_df["Total ARR"].max() if not sorted_df.empty else 0
    fig.update_layout(
        title="ARR per Rep", xaxis_title=None, yaxis_title=None,
        height=max(280, len(summary) * 55 + 80),
        margin=dict(l=10, r=10, t=30, b=20),
        xaxis=dict(tickprefix="$", tickformat=",.0f",
                   range=[0, max_val * 1.15] if max_val else None, **CHART_GRID),
        yaxis=dict(**CHART_GRID),
        **CHART_LAYOUT,
    )
    return fig

def build_count_chart(summary: pd.DataFrame, color: str):
    sorted_df = summary.sort_values("# Accounts", ascending=True)
    fig = px.bar(sorted_df, x="# Accounts", y="Rep Name", orientation="h",
                 text="# Accounts", color_discrete_sequence=[color])
    max_val = sorted_df["# Accounts"].max() if not sorted_df.empty else 0
    fig.update_traces(texttemplate="%{text}", textposition="inside",
                      textfont=dict(color="white", size=11), marker_line_width=0,
                      marker_opacity=0.9)
    fig.update_layout(
        title="Accounts per Rep", xaxis_title=None, yaxis_title=None,
        height=max(280, len(summary) * 55 + 80),
        margin=dict(l=10, r=10, t=30, b=20),
        xaxis=dict(range=[0, max_val * 1.15] if max_val else None, **CHART_GRID),
        yaxis=dict(**CHART_GRID),
        **CHART_LAYOUT,
    )
    return fig

def show_balance_metrics(summary: pd.DataFrame):
    if summary.empty:
        st.info("No accounts in this segment at the current threshold.")
        return
    arr_values = summary["Total ARR"]
    count_values = summary["# Accounts"]
    arr_spread = arr_values.max() - arr_values.min()
    count_spread = int(count_values.max() - count_values.min())
    equity_score = (1 - arr_values.std() / arr_values.mean()) * 100 if arr_values.mean() > 0 else 0
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("ARR Spread", f"${arr_spread:,.0f}")
    with m2:
        st.metric("Account Spread", f"{count_spread}")
    with m3:
        st.metric("ARR Equity Score", f"{equity_score:.1f}%")

def section_header(title: str, subtitle: str, color: str):
    st.markdown(
        f'<div class="section-header" style="border-color: {color};">'
        f"<h2>{title}</h2>"
        f"<p>{subtitle}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

def spacer(size: str = "md"):
    cls = "spacer-lg" if size == "lg" else "spacer"
    st.markdown(f'<div class="{cls}"></div>', unsafe_allow_html=True)

def format_summary_display(summary: pd.DataFrame) -> pd.DataFrame:
    display = summary.copy()
    display["Total ARR"] = display["Total ARR"].apply(lambda x: f"${x:,.0f}")
    display["Avg ARR per Account"] = display["Avg ARR per Account"].apply(lambda x: f"${x:,.0f}")
    return display

# =====================================================
# MAIN CONTENT
# =====================================================

# --- Segmentation Overview ---
section_header("Segmentation Overview",
               "Account classification based on employee count threshold",
               ACCENT_ORANGE)
spacer()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Accounts", f"{len(accounts_df):,}")
    st.caption(f"Total ARR: ${accounts_df['ARR'].sum():,.0f}")
with col2:
    st.metric("Enterprise Accounts", f"{len(enterprise_df):,}")
    st.caption(f"ARR: ${enterprise_df['ARR'].sum():,.0f}")
with col3:
    st.metric("Mid-Market Accounts", f"{len(midmarket_df):,}")
    st.caption(f"ARR: ${midmarket_df['ARR'].sum():,.0f}")

st.markdown("---")

# --- Enterprise Distribution ---
section_header("🏢 Enterprise Territory Distribution",
               f"{len(enterprise_reps)} reps · {len(enterprise_df)} accounts",
               ENTERPRISE_COLOR)
spacer()

ent_summary = build_summary(enterprise_assigned)

ent_left, ent_right = st.columns(2)
with ent_left:
    st.plotly_chart(build_arr_chart(ent_summary, ENTERPRISE_COLOR), use_container_width=True)
with ent_right:
    st.plotly_chart(build_count_chart(ent_summary, ENTERPRISE_COLOR), use_container_width=True)

spacer()
show_balance_metrics(ent_summary)
spacer()
st.dataframe(format_summary_display(ent_summary), use_container_width=True, hide_index=True)

st.markdown("---")

# --- Mid-Market Distribution ---
section_header("🏬 Mid-Market Territory Distribution",
               f"{len(midmarket_reps)} reps · {len(midmarket_df)} accounts",
               MIDMARKET_COLOR)
spacer()

mm_summary = build_summary(midmarket_assigned)

mm_left, mm_right = st.columns(2)
with mm_left:
    st.plotly_chart(build_arr_chart(mm_summary, MIDMARKET_COLOR), use_container_width=True)
with mm_right:
    st.plotly_chart(build_count_chart(mm_summary, MIDMARKET_COLOR), use_container_width=True)

spacer()
show_balance_metrics(mm_summary)
spacer()
st.dataframe(format_summary_display(mm_summary), use_container_width=True, hide_index=True)

st.markdown("---")

# --- Location Insights ---
section_header("🌎 Location Insights",
               "Revenue concentration and account distribution by state",
               ACCENT_PURPLE)
spacer()

all_assigned = pd.concat([enterprise_assigned, midmarket_assigned], ignore_index=True)

location_segment = (
    all_assigned.groupby(["Location", "Assigned_Segment"])["ARR"]
    .sum().reset_index()
)
location_segment.columns = ["State", "Segment", "Total ARR"]
location_order = (location_segment.groupby("State")["Total ARR"]
                  .sum().sort_values(ascending=False).index.tolist())

fig_loc = px.bar(
    location_segment, x="State", y="Total ARR", color="Segment",
    barmode="group",
    color_discrete_map={"Enterprise": ENTERPRISE_COLOR, "Mid-Market": MIDMARKET_COLOR},
    category_orders={"State": location_order},
    text="Total ARR",
)
fig_loc.update_traces(texttemplate="$%{text:,.0f}", textposition="outside",
                      textfont_size=9, marker_opacity=0.9, marker_line_width=0)
fig_loc.update_layout(
    title="ARR by State", xaxis_title=None, yaxis_title=None,
    yaxis=dict(tickprefix="$", tickformat=",.0f", **CHART_GRID),
    xaxis=dict(**CHART_GRID),
    height=420,
    margin=dict(t=20, b=30, l=10, r=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(size=11)),
    **CHART_LAYOUT,
)
st.plotly_chart(fig_loc, use_container_width=True)

spacer()

state_summary = (
    all_assigned.groupby("Location")
    .agg(
        Total_Accounts=("Account_ID", "count"),
        Enterprise_Accounts=("Assigned_Segment", lambda x: (x == "Enterprise").sum()),
        MidMarket_Accounts=("Assigned_Segment", lambda x: (x == "Mid-Market").sum()),
        Total_ARR=("ARR", "sum"),
        Avg_Risk_Score=("Risk_Score", "mean"),
    )
    .reset_index()
    .sort_values("Total_ARR", ascending=False)
)
state_summary.columns = [
    "State", "Total Accounts", "Enterprise Accounts",
    "Mid-Market Accounts", "Total ARR", "Avg Risk Score",
]

state_display = state_summary.copy()
state_display["Total ARR"] = state_display["Total ARR"].apply(lambda x: f"${x:,.0f}")
state_display["Avg Risk Score"] = state_display["Avg Risk Score"].apply(lambda x: f"{x:.1f}")
st.dataframe(state_display, use_container_width=True, hide_index=True)

st.markdown("---")

# --- Export ---
section_header("📥 Export Assignments",
               "Download the full assignment mapping as CSV",
               "#52525b")
spacer()

export_df = pd.concat([enterprise_assigned, midmarket_assigned], ignore_index=True)
export_df = export_df.rename(columns={
    "Assigned_Segment": "Segment",
    "Current_Rep": "Previous_Rep",
})[
    ["Account_ID", "Account_Name", "Segment", "Assigned_Rep",
     "Previous_Rep", "ARR", "Num_Employees", "Num_Marketers",
     "Risk_Score", "Location"]
].sort_values("Account_ID")

changed = (export_df["Assigned_Rep"] != export_df["Previous_Rep"]).sum()
st.markdown(
    f"**{changed}** of **{len(export_df)}** accounts changed reps "
    f"({changed / len(export_df) * 100:.1f}%)"
)

spacer()

st.download_button(
    label="Download territory_assignments.csv",
    data=export_df.to_csv(index=False),
    file_name="territory_assignments.csv",
    mime="text/csv",
)
