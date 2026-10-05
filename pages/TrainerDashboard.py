import streamlit as st 
from helper import login_status_check
from helper import role_check
import requests
login_status_check() 
role_check("trainer")        




st.title("trainer dashboard")

loggedin_Triner_name=st.session_state["name"]
loggedin_Triner_email=st.session_state["email"]
loggedin_Triner_role=st.session_state["role"]
loggedin_Triner_id=st.session_state["id"]


st.write("name",loggedin_Triner_name)
st.write("email",loggedin_Triner_email)
st.write("role",loggedin_Triner_role)

st.divider()


st.subheader("trainer features")
c1,c2=st.columns(2)

with c1:
    if st.button("AddCourse"):
        st.session_state["addCourse_status"]=True

with c2:
    if st.button("ViewMyCourses"):
        st.session_state["ViewMyCourses_status"]=True
    

if st.session_state.get("addCourse_status",False):
    st.title("add course Form")
    with st.form("addCourseForm"):
        course_name = st.text_input(
            "Course Name"
        )

        description = st.text_area(
            "Course Description"
        )

        duration = st.text_input(
            "Course Duration",
            placeholder="Example: 3 Months"
        )

        cl1,cl2=st.columns(2)

        with cl1:
            if st.form_submit_button("addCourse"):
                new_course={
                    "trainer_id":loggedin_Triner_id,
                    "course_name":course_name,
                    "course_description":description,
                    "course_duration":duration,
                }
                res=requests.post("http://127.0.0.1:8000/add_course",json=new_course)
                if res.status_code == 200:
                    res_obj=res.json()
                    st.write(res_obj)
                else:
                    st.write("some issue occured")    


if st.session_state.get("ViewMyCourses_status",False):
    res=requests.get("http://127.0.0.1:8000/get_my_courses",
    params={"t_id":loggedin_Triner_id})
    if res.status_code==200:
        res_obj=res.json()
        st.dataframe(res_obj["data"])
    else:
        st.write("some occure occured")


       
