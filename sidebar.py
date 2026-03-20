import streamlit as st
import pandas as pd
def load_css():
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

def sidebar():
    

    with st.sidebar:

        # ---------------- LOGO ----------------
        st.image("New_logo-removebg-preview.png")

        st.divider()

        # ---------------- PROFILE ----------------
        st.subheader("Profile")
        st.write(f"Name: {st.session_state.username}")
        st.write(f"Role: {st.session_state.role}")

        st.divider()

        # ---------------- FILTERS ----------------
        st.subheader("Filters")

        page = st.session_state.page

        filters = st.session_state.get("filters", {})

        # ---------------- EXECUTIVE ----------------
        if  st.session_state.page== "executive":

            data = pd.read_csv("data/modified_dataset.csv")
            data["Claim_Submission_Date"] = pd.to_datetime(
                data["Claim_Submission_Date"], format="%d-%m-%Y"
            )

            min_date = data["Claim_Submission_Date"].min()
            max_date = data["Claim_Submission_Date"].max()

            filters["date_range"] = st.date_input(
                "Date Range",
                value=filters.get("date_range", (min_date, max_date)),
                min_value=min_date,
                max_value=max_date
            )

            role = st.session_state.role
            user_department = st.session_state.department

# ---------------- DEPARTMENT FILTER ----------------
            if role in ["CFO", "RCM"]:
                filters["department_filter"] = st.selectbox(
                "Department",
                ["All"] + list(data["Department"].unique()),
                index=0
            )

            if role == "Department Head":
                filters["department_filter"] = user_department
                st.info(f"Department: {user_department}")

            filters["insurance_filter"] = st.selectbox(
                "Insurance",
                ["All"] + list(data["Insurance_Type"].unique())
            )

        # ---------------- REVENUE LEAKAGE ----------------
        if st.session_state.page == "revenue_leakage":

            data = pd.read_csv("data/modified_dataset.csv")
            data["Claim_Submission_Date"] = pd.to_datetime(
                data["Claim_Submission_Date"], format="%d-%m-%Y"
            )

            min_date = data["Claim_Submission_Date"].min()
            max_date = data["Claim_Submission_Date"].max()

            filters["date_range"] = st.date_input(
                "Date Range",
                value=filters.get("date_range", (min_date, max_date)),
                min_value=min_date,
                max_value=max_date
            )

            role = st.session_state.role
            user_department = st.session_state.department

# ---------------- DEPARTMENT FILTER ----------------
            if role in ["CFO", "RCM"]:
                filters["department_filter"] = st.selectbox(
                "Department",["All"] + list(data["Department"].unique()),
                index=0
                )

            if role == "Department Head":
                filters["department_filter"] = user_department
                st.info(f"Department: {user_department}")

            filters["insurance_filter"] = st.selectbox(
                "Insurance",
                ["All"] + list(data["Insurance_Type"].unique())
            )

        # ---------------- FORECAST ----------------
        # if st.session_state.page == "forecast":

        #     data = pd.read_csv("data/monthly_revenue_history.csv")
        #     data["Month"] = pd.to_datetime(data["Month"])

        #     min_date = data["Month"].min()
        #     max_date = data["Month"].max()

        #     filters["date_range"] = st.date_input(
        #         "Date Range",
        #         value=filters.get("date_range", (min_date, max_date)),
        #         min_value=min_date,
        #         max_value=max_date
        #     )

        if st.session_state.page == "claim_denial":
            data = pd.read_csv("data/pre_processed_data.csv")
            role = st.session_state.role
            user_department = st.session_state.department

            filters["risk_filter"] = st.selectbox(
                "Risk Level",
                ["All", "Low", "Medium", "High"]
            )

            if role in ["CFO", "RCM"]:
                filters["department_filter"] = st.selectbox(
                "Department",["All"] + list(data["Department"].unique()),
                index=0
                )

            if role == "Department Head":
                filters["department_filter"] = user_department
                st.info(f"Department: {user_department}")

            filters["insurance_filter"] = st.selectbox(
                "Insurance",
                ["All"] + list(data["Insurance_Type"].unique())
            )

            if st.session_state.page == "billing_anomaly":

                data = pd.read_csv("data/modified_dataset.csv")

                data["Claim_Submission_Date"] = pd.to_datetime(
                data["Claim_Submission_Date"],
                dayfirst=True,
                errors="coerce"
                )

                min_date = data["Claim_Submission_Date"].min()
                max_date = data["Claim_Submission_Date"].max()

            # Date filter
                filters["date_range"] = st.date_input(
                "Date Range",
                value=filters.get("date_range", (min_date, max_date)),
                min_value=min_date,
                max_value=max_date
                )

                role = st.session_state.get("role")
                user_department = st.session_state.get("department")

                # Department filter (Role-based)
                if role in ["CFO", "RCM"]:
                    filters["department_filter"] = st.selectbox(
                    "Department",
                    ["All"] + list(data["Department"].unique())
                )
                else:
                    filters["department_filter"] = user_department
                    st.info(f"Department: {user_department}")

            # Insurance filter
                filters["insurance_filter"] = st.selectbox(
                    "Insurance",
                    ["All"] + list(data["Insurance_Type"].unique())
                )


        # ---------------- DEFAULT ----------------
        else:
            filters = {}

        st.divider()

        # ---------------- NAVIGATION ----------------
        st.subheader("Navigation")
        role = st.session_state.role

        page_changed = False

        if st.button("Executive Overview"):
            st.session_state.page = "executive"
            page_changed = True

        if st.button("Revenue Leakage Analysis"):
            st.session_state.page = "revenue_leakage"
            page_changed = True

        if st.button("Claim Denial Risk Prediction"):
            st.session_state.page = "claim_denial"
            page_changed = True
        if role != "Department Head":
            if st.button("Revenue Forecasting"):
                st.session_state.page = "forecast"
                page_changed = True

        if st.button("Billing Anamoly Detection"):
            st.session_state.page = "billing_anomaly"
            page_changed = True

        st.divider()

        # ---------------- LOGOUT ----------------
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "executive"
            st.rerun()
