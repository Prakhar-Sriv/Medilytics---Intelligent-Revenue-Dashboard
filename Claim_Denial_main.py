import streamlit as st
import pandas as pd
import plotly.express as px

def claim_denial():

    # -------- LOAD CSS -------- #
    def load_css():
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    load_css()

    # ---------------- CHART STYLE ---------------- #
    def clean_chart(fig):
        fig.update_layout(
            height=500,
            plot_bgcolor="#334155",
            paper_bgcolor="#334155",
            font=dict(color="white", size=14),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=40, r=40, t=40, b=110)
        )
        return fig

    # ---------------- TITLE ---------------- #
    st.markdown("""
    <h1 style='text-align:center; font-weight:700;'>
    <span style="color:#FFEA00;">Medlytics AI</span>
    <span style="color:white;"> – Claim Denial Risk Prediction Dashboard</span>
    </h1>
    """, unsafe_allow_html=True)

    # ---------------- LOAD DATA ---------------- #
    predictions = pd.read_csv("data/denial_model_predictions.csv")
    data = pd.read_csv("data/pre_processed_data.csv")
    feature_importance = pd.read_csv("data/denial_feature_importance.csv")

    merged = data.merge(predictions, on="Claim_ID")

    # ---------------- APPLY SIDEBAR FILTERS ---------------- #
    filters = st.session_state.get("filters", {})

    filtered_data = merged.copy()

    # Risk filter
    if filters.get("risk_filter") and filters.get("risk_filter") != "All":
        filtered_data = filtered_data[
            filtered_data["Risk_Level"] == filters["risk_filter"]
        ]

    # Department filter
    if filters.get("department_filter") and filters.get("department_filter") != "All":
        filtered_data = filtered_data[
            filtered_data["Department"] == filters["department_filter"]
        ]

    # Insurance filter
    if filters.get("insurance_filter") and filters.get("insurance_filter") != "All":
        filtered_data = filtered_data[
            filtered_data["Insurance_Type"] == filters["insurance_filter"]
        ]

    # ---------------- SAFETY CHECK ---------------- #
    if filtered_data.empty:
        st.error("No data available for selected filters.")
        return

    # ---------------- KPI CALCULATIONS ---------------- #
    high_risk_df = filtered_data[filtered_data["Risk_Level"] == "High"]

    # SAFE CALCULATIONS
    if not high_risk_df.empty:

        top_risk_dept = high_risk_df["Department"].value_counts().idxmax()
        top_risk_insurance = high_risk_df["Insurance_Type"].value_counts().idxmax()

        potential_revenue_loss = high_risk_df["Claim_Amount"].sum()
        highest_risk_claim = high_risk_df["Claim_Amount"].max()

    else:
        top_risk_dept = "N/A"
        top_risk_insurance = "N/A"
        potential_revenue_loss = 0
        highest_risk_claim = 0

    # Continue calculations
    potential_revenue_loss_cr = potential_revenue_loss / 10000000
    highest_risk_claim_k = highest_risk_claim / 1000

    # Best department (safe)
    if not filtered_data.empty:
        dept_avg_prob = filtered_data.groupby("Department")["Denial_Probability"].mean()
        best_dept = dept_avg_prob.idxmin()
    else:
        best_dept = "N/A"

    # ---------------- KPI DISPLAY ---------------- #
    st.subheader("Operational Risk Indicators")

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Denial Risk Concentration</div>
        <div class="metric-value">{top_risk_dept}</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Highest Risk Insurance</div>
        <div class="metric-value">{top_risk_insurance}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Potential Revenue Loss</div>
        <div class="metric-value">₹{potential_revenue_loss_cr:,.2f} Cr</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Highest Risk Claim Value</div>
        <div class="metric-value">₹{highest_risk_claim_k:,.2f} K</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-title">Best Performing Department</div>
        <div class="metric-value">{best_dept}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- CHARTS ---------------- #
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Denial Risk by Insurance Type")
        insurance_risk = filtered_data.groupby("Insurance_Type")["Denial_Probability"].mean().reset_index()
        fig1 = px.bar(insurance_risk, x="Insurance_Type", y="Denial_Probability")
        st.plotly_chart(clean_chart(fig1), use_container_width=True)

    with col2:
        st.subheader("Claims at Risk by Department")
        dept_risk = filtered_data.groupby(["Department", "Risk_Level"]).size().reset_index(name="Count")
        fig2 = px.bar(dept_risk, x="Department", y="Count", color="Risk_Level", barmode="stack")
        st.plotly_chart(clean_chart(fig2), use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Denial Risk Trend Over Time")
        filtered_data["Claim_Date"] = pd.to_datetime(
            filtered_data["Claim_Submission_Date"],
            dayfirst=True,
            errors="coerce"
        )
        filtered_data["Year_Month"] = filtered_data["Claim_Date"].dt.to_period("M").astype(str)

        trend_data = filtered_data.groupby("Year_Month")["Denial_Probability"].mean().reset_index()
        fig3 = px.line(trend_data, x="Year_Month", y="Denial_Probability", markers=True)
        st.plotly_chart(clean_chart(fig3), use_container_width=True)

    with col4:
        st.subheader("Claim Risk Level Distribution")
        risk_counts = filtered_data["Risk_Level"].value_counts().reset_index()
        risk_counts.columns = ["Risk_Level", "Count"]
        fig4 = px.pie(risk_counts, names="Risk_Level", values="Count", hole=0.5)
        st.plotly_chart(clean_chart(fig4), use_container_width=True)

    # ---------------- TABLE ---------------- #
    st.subheader("Risk Claims Requiring Review")

    filtered_data["Denial_Probability"] = pd.to_numeric(
        filtered_data["Denial_Probability"],
        errors="coerce"
    )

    top_claims = filtered_data.sort_values(
        "Denial_Probability",
        ascending=False
    ).head(10)

    display_table = top_claims[
        ["Claim_ID", "Denial_Probability", "Risk_Level"]
    ].rename(columns={"Denial_Probability": "Risk_Score"})

    st.dataframe(display_table, use_container_width=True)
