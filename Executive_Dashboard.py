import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import time



# ---------------------------------------
# PAGE CONFIG + THEME
# ---------------------------------------
st.set_page_config(page_title="Medilytics Executive Dashboard", layout="wide")
pio.templates.default = "plotly_dark"

def load_css():
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# ---------------------------------------
# MAIN FUNCTION
# ---------------------------------------
def show_dashboard():

    # ---------------------------------------
    # LOAD DATA
    # ---------------------------------------
    data = pd.read_csv(r"data\modified_dataset.csv")

    # Convert date properly (robust fix)
    data["Claim_Submission_Date"] = pd.to_datetime(
        data["Claim_Submission_Date"],
        dayfirst=True,
        errors="coerce"
    )

    role = st.session_state.get("role", "User")
    user_department = st.session_state.get("department", "Unknown")

    if role == "Department Head":
        data = data[data["Department"] == user_department]


    # ---------------------------------------
    # APPLY FILTERS (FIXED VERSION)
    # ---------------------------------------
    filtered = data.copy()
    filters = st.session_state.get("filters", {})

    # DATE FILTER
    if "date_range" in filters and filters["date_range"]:
        start, end = filters["date_range"]

        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        filtered = filtered[
            (filtered["Claim_Submission_Date"] >= start) &
            (filtered["Claim_Submission_Date"] <= end)
        ]

    # INSURANCE FILTER
    if filters.get("insurance") and filters["insurance"] != "All":
        filtered = filtered[
            filtered["Insurance_Type"] == filters["insurance"]
        ]

    # DEPARTMENT FILTER
    if filters.get("department") and filters["department"] != "All":
        filtered = filtered[
            filtered["Department"] == filters["department"]
        ]


    # ---------------------------------------
    # KPI CALCULATIONS (SAFE)
    # ---------------------------------------
    total_revenue = filtered["Actual_Revenue"].sum()
    net_revenue = filtered["Payment_Received"].sum()
    avg_revenue = filtered["Actual_Revenue"].mean()

    if len(filtered) > 0:
        approval_rate = (
            (filtered["Denial_Flag"] == 0).sum() / len(filtered)
        ) * 100
    else:
        approval_rate = 0

    revenue_leakage = (
        filtered["Expected_Revenue"].sum()
        - filtered["Actual_Revenue"].sum()
    )


    # ---------------------------------------
    # ANIMATED METRIC
    # ---------------------------------------
    def animated_metric(label, value, prefix="₹", suffix=""):
        placeholder = st.empty()

        steps = 30
        increment = value / steps if steps != 0 else 0
        current = 0

        for _ in range(steps):
            current += increment
            placeholder.metric(label, f"{prefix}{int(current):,}{suffix}")
            time.sleep(0.01)

        placeholder.metric(label, f"{prefix}{int(value):,}{suffix}")


    # ---------------------------------------
    # HEADER
    # ---------------------------------------
    st.title("Medilytics : Intelligent Revenue Dashboard")
    st.divider()


    # ---------------------------------------
    # KPI ROW
    # ---------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.subheader("Total Revenue")
        animated_metric("", total_revenue)

    with c2:
        st.subheader("Net Revenue")
        animated_metric("", net_revenue)

    with c3:
        st.subheader("Approval Rate")
        animated_metric("", approval_rate, prefix="", suffix="%")

    with c4:
        st.subheader("Revenue Leakage")
        animated_metric("", revenue_leakage)

    st.divider()


    # ---------------------------------------
    # CHART DATA
    # ---------------------------------------
    monthly_rev = (
        filtered
        .groupby(filtered["Claim_Submission_Date"].dt.to_period("M"))["Actual_Revenue"]
        .sum()
        .reset_index()
    )

    monthly_rev["Claim_Submission_Date"] = monthly_rev["Claim_Submission_Date"].astype(str)

    dept_rev = (
        filtered.groupby("Department")["Actual_Revenue"]
        .sum()
        .reset_index()
    )


    # ---------------------------------------
    # COLORS
    # ---------------------------------------
    colors = [
        "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
        "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"
    ]


    # ---------------------------------------
    # EXECUTIVE VIEW
    # ---------------------------------------
    if role in ["CFO", "RCM"]:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Monthly Revenue Trend")

            fig1 = px.line(
                monthly_rev,
                x="Claim_Submission_Date",
                y="Actual_Revenue",
                markers=True
            )

            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Revenue by Department")

            fig2 = px.bar(
                dept_rev,
                x="Department",
                y="Actual_Revenue",
                color="Department",
                color_discrete_sequence=colors
            )

            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        t1, t2 = st.columns(2)

        with t1:
            st.subheader("Top Revenue Departments")

            top_dept = (
                filtered.groupby("Department")["Actual_Revenue"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )

            st.dataframe(top_dept.head(10), use_container_width=True)

        with t2:
            st.subheader("Outstanding Claims")

            outstanding = filtered[
                filtered["Payment_Received"] < filtered["Actual_Revenue"]
            ]

            st.dataframe(
                outstanding[["Claim_ID", "Department", "Actual_Revenue", "Payment_Received"]].head(10),
                use_container_width=True
            )


    # ---------------------------------------
    # DEPARTMENT VIEW
    # ---------------------------------------
    else:

        st.subheader(f"Monthly Revenue Trend — {user_department}")

        monthly_rev = (
            filtered.groupby("Month")["Actual_Revenue"]
            .sum()
            .reset_index()
        )

        fig1 = px.line(
            monthly_rev,
            x="Month",
            y="Actual_Revenue",
            markers=True
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.divider()

        # Revenue by Doctor
        st.subheader("Revenue by Doctor")

        doctor_rev = (
            filtered.groupby("Doctor_Name")["Actual_Revenue"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig2 = px.bar(
            doctor_rev,
            x="Doctor_Name",
            y="Actual_Revenue",
            color="Doctor_Name",
            color_discrete_sequence=colors
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # Top Doctors
        st.subheader("Top Revenue Generating Doctors")

        top_doctors = doctor_rev.head(10)

        st.dataframe(top_doctors, use_container_width=True)

        # Recent Claims
        st.subheader("Recent Claims")

        st.dataframe(
            filtered[
                ["Claim_ID", "Doctor_Name", "Actual_Revenue", "Payment_Received", "Insurance_Type"]
            ].head(15),
            use_container_width=True
        )
