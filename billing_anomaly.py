import streamlit as st
import pandas as pd
import plotly.express as px

def load_css():
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


def billing_anomaly():

    st.markdown("""
    <h1 style='text-align:center; color:#FFD700;'>Billing Anomaly Detection</h1>
    """, unsafe_allow_html=True)

    # ---------------- LOAD DATA ---------------- #
    data = pd.read_csv("data/modified_dataset.csv")

    # ---------------- APPLY SIDEBAR FILTERS ---------------- #
    filters = st.session_state.get("filters", {})

    filtered_data = data.copy()

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

    # Date filter
    if filters.get("date_range") and len(filters["date_range"]) == 2:
        start, end = pd.to_datetime(filters["date_range"][0]), pd.to_datetime(filters["date_range"][1])

        filtered_data["Claim_Submission_Date"] = pd.to_datetime(
            filtered_data["Claim_Submission_Date"],
            dayfirst=True,
            errors="coerce"
        )

        filtered_data = filtered_data[
            (filtered_data["Claim_Submission_Date"] >= start) &
            (filtered_data["Claim_Submission_Date"] <= end)
        ]

    # ---------------- SAFETY CHECK ---------------- #
    if filtered_data.empty:
        st.warning("No data available for selected filters.")
        return

    # ---------------- ANOMALY DETECTION ---------------- #
    mean_val = filtered_data["Claim_Amount"].mean()
    std_val = filtered_data["Claim_Amount"].std()

    threshold = mean_val + 2 * std_val

    filtered_data["Anomaly"] = filtered_data["Claim_Amount"] > threshold

    anomaly_data = filtered_data[filtered_data["Anomaly"] == True]

    # ---------------- KPI SECTION ---------------- #
    st.subheader("Anomaly Insights")

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("Total Claims", len(filtered_data))

    with k2:
        st.metric("Anomalous Claims", len(anomaly_data))

    with k3:
        anomaly_percent = (len(anomaly_data) / len(filtered_data)) * 100
        st.metric("Anomaly %", f"{anomaly_percent:.2f}%")

    st.divider()

    # ---------------- CHARTS ---------------- #
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Claim Amount Distribution")
        fig1 = px.histogram(filtered_data, x="Claim_Amount", nbins=30)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Anomaly vs Normal")
        anomaly_counts = filtered_data["Anomaly"].value_counts().reset_index()
        anomaly_counts.columns = ["Type", "Count"]

        fig2 = px.pie(anomaly_counts, names="Type", values="Count")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- ANOMALY TABLE ---------------- #
    st.subheader("Top Anomalous Claims")

    if anomaly_data.empty:
        st.info("No anomalies detected for selected filters.")
    else:
        top_anomalies = anomaly_data.sort_values(
            "Claim_Amount", ascending=False
        ).head(10)

        st.dataframe(top_anomalies, use_container_width=True)
