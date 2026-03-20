import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_css():
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


def revenue():

    # ---------------- STYLE ----------------
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg,#0f172a,#020617);
            color: #e2e8f0;;
        }

        .main-title {
            text-align: center;
            color: #FFD700;
            font-size: 32px;
            font-weight: 800;
            padding: 10px;
        }

        .kpi-card {
            background: linear-gradient(145deg, #16263A, #1E2D40);
            padding: 22px;
            border-radius: 12px;
            border: 1px solid #243B55;
            text-align: center;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
        }

        .kpi-title {
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .kpi-value {
            font-size: 28px;
            font-weight: 800;
            color: white;
        }

        .c1 { color: #00E5FF; }
        .c2 { color: #FF5E5E; }
        .c3 { color: #FFD700; }
        .c4 { color: #00FF87; }
    </style>
    """, unsafe_allow_html=True)

    # ---------------- HELPERS ----------------
    def format_indian_number(num):
        num = float(num)
        if num >= 1_00_00_000:
            return f"{num/1_00_00_000:.1f}Cr"
        elif num >= 1_00_000:
            return f"{num/1_00_000:.1f}L"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.0f}"

    def apply_style(fig):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FFFFFF", size=12),
            margin=dict(l=40, r=20, t=30, b=40)
        )
        return fig

    # ---------------- LOAD DATA ----------------
    @st.cache_data
    def load_data():
        data = pd.read_csv("data/cleaned_claim_dataset.csv")
        data["Claim_Submission_Date"] = pd.to_datetime(
            data["Claim_Submission_Date"],
            format="%d-%m-%Y",
            errors="coerce"
        )
        data["Revenue_Leakage"] = (
            data["Expected_Revenue"] - data["Actual_Revenue"]
        ).fillna(0)
        return data

    data = load_data()
    role = st.session_state.role

    # ---------------- APPLY SIDEBAR FILTERS ----------------
    filters = st.session_state.get("filters", {})

    filtered_data = data.copy()

    # Date filter
    if "date_range" in filters:
        start, end = filters["date_range"]
        filtered_data = filtered_data[
            (filtered_data["Claim_Submission_Date"] >= pd.to_datetime(start)) &
            (filtered_data["Claim_Submission_Date"] <= pd.to_datetime(end))
        ]

    # Department filter
    if filters.get("department_filter") != "All":
        filtered_data = filtered_data[
            filtered_data["Department"] == filters["department_filter"]
        ]

    # Insurance filter
    if filters.get("insurance_filter") != "All":
        filtered_data = filtered_data[
            filtered_data["Insurance_Type"] == filters["insurance_filter"]
        ]

    # ---------------- UI ----------------
    st.markdown('<div class="main-title">REVENUE LEAKAGE ANALYSIS</div>', unsafe_allow_html=True)

    if filtered_data.empty:
        st.error("No Data Found")
        return

    # ---------------- KPIs ----------------
    total_claims = len(filtered_data)
    total_leakage = filtered_data['Revenue_Leakage'].sum()
    avg_leakage = filtered_data['Revenue_Leakage'].mean()
    top_dept = filtered_data.groupby("Department")["Revenue_Leakage"].sum().idxmax()

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title c1'>TOTAL CLAIMS</div><div class='kpi-value'>{format_indian_number(total_claims)}</div></div>", unsafe_allow_html=True)

    with k2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title c2'>TOTAL LEAKAGE</div><div class='kpi-value'>₹{format_indian_number(total_leakage)}</div></div>", unsafe_allow_html=True)

    with k3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-title c3'>AVG LEAKAGE</div><div class='kpi-value'>₹{format_indian_number(avg_leakage)}</div></div>", unsafe_allow_html=True)

    with k4:
        if role != "Department Head":
            st.markdown(f"<div class='kpi-card'><div class='kpi-title c4'>TOP LOSS DEPT</div><div class='kpi-value'>{top_dept}</div></div>", unsafe_allow_html=True)

    st.divider()

    # ---------------- CHARTS ----------------
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1:
        dept_data = filtered_data.groupby("Department")["Revenue_Leakage"].sum().reset_index()
        fig1 = px.bar(dept_data, x="Revenue_Leakage", y="Department", orientation='h')
        st.plotly_chart(apply_style(fig1), use_container_width=True)

    with c2:
        trend_data = filtered_data.copy()
        trend_data["Month"] = trend_data["Claim_Submission_Date"].dt.to_period("M").astype(str)
        trend_grouped = trend_data.groupby("Month")[["Revenue_Leakage", "Actual_Revenue"]].sum().reset_index()

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=trend_grouped["Month"], y=trend_grouped["Actual_Revenue"], fill='tozeroy', name='Actual'))
        fig2.add_trace(go.Scatter(x=trend_grouped["Month"], y=trend_grouped["Revenue_Leakage"], fill='tozeroy', name='Loss'))

        st.plotly_chart(apply_style(fig2), use_container_width=True)

    with c3:
        ins_data = filtered_data.groupby("Insurance_Type")["Revenue_Leakage"].sum().reset_index()
        fig3 = px.pie(ins_data, values="Revenue_Leakage", names="Insurance_Type", hole=0.5)
        st.plotly_chart(apply_style(fig3), use_container_width=True)

    with c4:
        fig4 = px.histogram(filtered_data, x="Revenue_Leakage", nbins=30)
        st.plotly_chart(apply_style(fig4), use_container_width=True)

    # ---------------- TABLE ----------------
    st.subheader("High-Leakage Claim Details")
    st.dataframe(
        filtered_data.sort_values(by="Revenue_Leakage", ascending=False).head(10),
        use_container_width=True
    )
