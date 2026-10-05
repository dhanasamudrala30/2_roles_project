import streamlit as st 
def login_status_check():
    if not st.session_state.get("status",False):
        st.title("login first")
        st.switch_page("app.py")


def role_check(incoming_role):
    if st.session_state.get("role","") != incoming_role  : 
        st.title("access denied")
        st.stop()