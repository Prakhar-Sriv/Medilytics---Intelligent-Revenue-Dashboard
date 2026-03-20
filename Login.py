import streamlit as st
import pandas as pd
from PIL import Image
def load_css():
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
def show_login():
    # Load logo
    logo_path = r"C:\Users\Prakhar\Downloads\New_logo-removebg-preview.png"
    logo = Image.open(logo_path)

    # Load users database
    users = pd.read_csv(r"data\users.csv")
  
    # Session states
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "role" not in st.session_state:
        st.session_state.role = None

    if "username" not in st.session_state:
        st.session_state.username = None

    if "department" not in st.session_state:
        st.session_state.department = None

    if "page" not in st.session_state:
        st.session_state.page = "executive"
    
    if "filters" not in st.session_state:
        st.session_state.filters={}


    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        if not st.session_state.logged_in:

            l1, l2, l3 = st.columns([1,2,1])

            with l2:
                st.image(logo)

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            st.write("")

            if st.button("Login", use_container_width=True):

                # Check credentials in CSV
                user = users[
                    (users["username"] == username) &
                    (users["password"] == password)
                ]

                if not user.empty:

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = user.iloc[0]["role"]
                    st.session_state.department = user.iloc[0]["department"]

                    st.success("Login successful")
                    st.rerun()

                else:
                    st.error("Invalid Username or Password")

        else:

            st.success(f"Welcome {st.session_state.username}")

            role = st.session_state.role

 
