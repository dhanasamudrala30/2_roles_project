import streamlit as st 
from helper import login_status_check
from helper import role_check

login_status_check()
role_check("student")

st.title("student dashboard")