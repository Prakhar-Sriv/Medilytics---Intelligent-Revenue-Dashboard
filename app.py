# import streamlit as st
# from Login import show_login
# from Executive_Dashboard import show_dashboard

# st.set_page_config(page_title="Medilytics", layout="wide")

# # Initialize session state
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# # Navigation logic
# if not st.session_state.logged_in:
#     show_login()

# else:
#     show_dashboard()


import streamlit as st
from Login import show_login
from Executive_Dashboard import show_dashboard
from sidebar import sidebar

st.set_page_config(page_title="Medilytics", layout="wide")


# Session state init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "executive"

# if "date_range" not in st.session_state:
#     st.session_state.date_range = (min_date, max_date)


# Routing
if not st.session_state.logged_in:
    show_login()

else:
    #  CALL SIDEBAR HERE
    sidebar()

    #  PAGE ROUTING HERE
    if st.session_state.page == "executive":
        show_dashboard()

    elif st.session_state.page == "forecast":
        from forecast_dashboard import revenue_forecast_model
        revenue_forecast_model()

    elif st.session_state.page == "revenue_leakage":
        from Revenue_Leakage_Analysis import revenue
        revenue()

    elif st.session_state.page == "claim_denial":
        from Claim_Denial_main import claim_denial
        claim_denial()

    elif st.session_state.page == "billing_anomaly":
        from billing_anomaly import billing_anomaly
        billing_anomaly()
