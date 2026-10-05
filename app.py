# third part lib streamlit install 
# pip install requests

# requests is tyhird part py lib which is used to create apis and it is used to perform http requests with req methods

# post()
# get()
# put()
# delete()


# pip install streamlit
# streamlit ru/n command
# streamlit run filename.py
import streamlit as st
import requests

# requests.post(be_server_running_url,json=regustrered_data)

t1, t2 = st.tabs(["🔑 Login", "📝 Register"])

with t1:

    st.title("🌈 Login Form 📝")

    with st.form("Login Form"):

        e=st.text_input("📧 Email", placeholder="Enter email here")

        p=st.text_input(
            "🔒 Password",
            placeholder="Enter password here",
            type="password"
        )

        r=st.selectbox("🎭 Role", ["", "trainer", "student"])

        l_btn=st.form_submit_button("🚀 Login")

        if l_btn:
            login_cred_details={
                "email":e,
                "password":p,
                "role":r
            }

            res_from_sup_for_login=requests.post("http://127.0.0.1:8000/login",json=login_cred_details)

            # st.write(res_from_sup_for_login)
            if res_from_sup_for_login.status_code == 200:
                st.write(res_from_sup_for_login.json())
                r_data=res_from_sup_for_login.json()
                st.session_state["status"] =True
                st.session_state["name"]=r_data["loggedIn_user"]["name"]
                st.session_state["role"]=r_data["loggedIn_user"]["role"]
                st.session_state["email"]=r_data["loggedIn_user"]["email"]
                st.session_state["id"]=r_data["loggedIn_user"]["id"]

                if st.session_state["status"] :
                    if st.session_state["role"] =="trainer":
                        st.switch_page("pages/TrainerDashboard.py")

                    if st.session_state["role"] == "student":
                        st.switch_page("pages/StudentDashboard.py")
                        
                    
                    
            else:
                st.write("some error occured")    


with t2:

    st.title("🌈 Registration Form 📝")

    with st.form("Reg form"):

        n=st.text_input("👤 Name", placeholder="Enter name here")

        e=st.text_input("📧 Email", placeholder="Enter email here")

        p=st.text_input(
            "🔒 Password",
            placeholder="Enter password here",
            type="password"
        )

        c_p=st.text_input(
            "🔐 Confirm Password",
            placeholder="Re-enter password here",
            type="password"
        )

        r=st.selectbox("🎭 Role", ["", "trainer", "student"])

        r_btn=st.form_submit_button("🚀 Register")

        if r_btn:
            new_user={
                "name":n,
                "email":e,
                "password":p,
                "c_password":c_p,
                "role":r
            }
            res=requests.post("http://127.0.0.1:8000/register",json=new_user)

            if res.status_code == 200:
                st.write(res.json())
            else:
                st.write("some error occured")    



