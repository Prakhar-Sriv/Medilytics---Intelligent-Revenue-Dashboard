import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
def load_css():
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


def revenue_forecast_model():



    # ---------------- HEADER ----------------
    st.markdown("<h1>Revenue Forecasting</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # ---------------- LOAD DATA ----------------
    history = pd.read_csv("data/monthly_revenue_history.csv")
    forecast = pd.read_csv("data/revenue_forecast.csv")

    history["Month"] = pd.to_datetime(history["Month"])
    forecast["Month"] = pd.to_datetime(forecast["Month"])

    # ---------------- APPLY SIDEBAR FILTERS ----------------
    filters = st.session_state.get("filters", {})

    # Date filter
    if "date_range" in filters:
        start, end = filters["date_range"]
        start, end = pd.to_datetime(start), pd.to_datetime(end)

        history = history[
            (history["Month"] >= start) &
            (history["Month"] <= end)
        ]

    # Department filter (SAFE)
    if "department_filter" in filters and "Department" in history.columns:
        if filters["department_filter"] != "All":
            history = history[
                history["Department"] == filters["department_filter"]
            ]

    # Insurance filter (SAFE)
    if "insurance_filter" in filters and "Insurance_Type" in history.columns:
        if filters["insurance_filter"] != "All":
            history = history[
                history["Insurance_Type"] == filters["insurance_filter"]
            ]


    # ---------------- KPI METRICS ----------------
    col1, col2, col3, col4 = st.columns(4)

    current_revenue = history["Actual_Revenue"].iloc[-1]
    avg_revenue = history["Actual_Revenue"].mean()
    forecast_total = forecast["Forecast_Revenue"].sum()

    growth = ((forecast["Forecast_Revenue"].iloc[0] - current_revenue) / current_revenue) * 100

    col1.metric("Latest Monthly Revenue", f"₹{current_revenue:,.0f}")
    col2.metric("Average Monthly Revenue", f"₹{avg_revenue:,.0f}")
    col3.metric("6 Month Forecast", f"₹{forecast_total:,.0f}")
    col4.metric("Projected Growth", f"{growth:.2f}%")

    st.markdown("---")

    # ---------------- PLOT THEME ----------------
    MEDLYTICS_THEME = dict(
        layout=dict(
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            font=dict(color="#E5E7EB"),
            title_font=dict(color="#FFD700", size=22),
            xaxis=dict(gridcolor="#1F2937"),
            yaxis=dict(gridcolor="#1F2937"),
        )
    )

    # ---------------- FORECAST GRAPH ----------------
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=history["Month"],
            y=history["Actual_Revenue"],
            mode="lines+markers",
            name="Historical Revenue"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["Month"],
            y=forecast["Forecast_Revenue"],
            mode="lines+markers",
            name="Forecast Revenue",
            line=dict(dash="dash")
        )
    )

    fig.update_layout(
        title="Hospital Revenue Forecast",
        template=MEDLYTICS_THEME,
        xaxis_title="Month",
        yaxis_title="Revenue",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- GROWTH ANALYSIS ----------------
    forecast_growth = forecast.copy()
    forecast_growth["Growth %"] = forecast_growth["Forecast_Revenue"].pct_change() * 100

    fig_growth = px.bar(
        forecast_growth,
        x="Month",
        y="Growth %",
        title="Forecast Revenue Growth Rate",
        template=MEDLYTICS_THEME
    )

    st.plotly_chart(fig_growth, use_container_width=True)

    # ---------------- DISTRIBUTION ----------------
    fig_dist = px.histogram(
        forecast,
        x="Forecast_Revenue",
        nbins=10,
        title="Forecast Revenue Distribution",
        template=MEDLYTICS_THEME
    )

    st.plotly_chart(fig_dist, use_container_width=True)

    # ---------------- CUMULATIVE ----------------
    forecast["Cumulative_Revenue"] = forecast["Forecast_Revenue"].cumsum()

    fig_cum = px.area(
        forecast,
        x="Month",
        y="Cumulative_Revenue",
        title="Cumulative Forecast Revenue",
        template=MEDLYTICS_THEME
    )

    st.plotly_chart(fig_cum, use_container_width=True)

    # ---------------- TABLE ----------------
    st.subheader("Forecast Revenue Table")

    forecast_table = forecast.copy()
    forecast_table["Forecast_Revenue"] = forecast_table["Forecast_Revenue"].apply(lambda x: f"₹{x:,.0f}")

    st.dataframe(forecast_table, use_container_width=True)

    # ---------------- INSIGHTS ----------------
    st.subheader("Forecast Insights")

    latest = forecast["Forecast_Revenue"].iloc[0]
    last_hist = history["Actual_Revenue"].iloc[-1]

    if latest > last_hist:
        st.success("Revenue is expected to increase in the coming months.")
    else:
        st.warning("Revenue may decline. Financial planning adjustments may be required.")

    st.info("""
    This forecast uses an **ARIMA Time-Series Model** trained on historical hospital revenue.

    Predictions help leadership with:

    • Budget planning  
    • Resource allocation  
    • Financial risk monitoring  
    """)
