


import streamlit as st
import requests

from helper import login_status_check
from helper import role_check




login_status_check()
role_check("trainer")




loggedin_Trainer_name = st.session_state["name"]
loggedin_Trainer_email = st.session_state["email"]
loggedin_Trainer_role = st.session_state["role"]
loggedin_Trainer_id = st.session_state["id"]




st.title("👨‍🏫 Trainer Dashboard")

st.write("Name:", loggedin_Trainer_name)
st.write("Email:", loggedin_Trainer_email)
st.write("Role:", loggedin_Trainer_role)

st.divider()

st.subheader("📊 Dashboard Overview")

try:
    response = requests.get(
        "http://127.0.0.1:8000/get_my_courses",
        params={"t_id": loggedin_Trainer_id},
        timeout=10
    )
    response.raise_for_status()

    courses = response.json().get("data", [])

    total_courses = len(courses)

    published_courses = sum(
        1 for course in courses
        if course.get("status") == "published"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="📚 Total Courses",
            value=total_courses
        )

    with col2:
        st.metric(
            label="🚀 Published Courses",
            value=published_courses
        )

except requests.RequestException:
    st.error("Unable to load dashboard statistics. Please check your backend.")

st.divider()

st.subheader("🚀 Trainer Features")

c1, c2 = st.columns(2)



with c1:

    if st.button(
        "➕ Add Course",
        use_container_width=True
    ):
        st.session_state["addCourse_status"] = True
        st.session_state["ViewMyCourses_status"] = False



with c2:

    if st.button(
        "📚 View My Courses",
        use_container_width=True
    ):
        st.session_state["ViewMyCourses_status"] = True
        st.session_state["addCourse_status"] = False



if st.session_state.get("addCourse_status", False):

    st.divider()

    st.subheader("➕ Add Course Form")

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

        course_status = st.selectbox(
            "Course Status",
            ["draft", "published"],
            format_func=lambda status: {
                "draft": "📝 Draft — Not available to students",
                "published": "🚀 Published — Ready for students"
            }[status]
        )



        cl1, cl2 = st.columns(2)


       

        with cl1:

            add_course = st.form_submit_button(
                "➕ Add Course",
                use_container_width=True
            )

            if add_course:

                new_course = {
                    "trainer_id": loggedin_Trainer_id,
                    "course_name": course_name,
                    "course_description": description,
                    "course_duration": duration,
                    "status": course_status
                }

                res = requests.post(
                    "http://127.0.0.1:8000/add_course",
                    json=new_course
                )

                if res.status_code == 200:

                    res_obj = res.json()

                    st.success(
                        "✅ Course added successfully!"
                    )

                    st.write(res_obj)

                else:

                    st.error(f"Status Code: {res.status_code}")
                    st.code(res.text)


        

        with cl2:

            cancel = st.form_submit_button(
                "❌ Cancel",
                use_container_width=True
            )

            if cancel:

                st.session_state["addCourse_status"] = False

                st.rerun()


if st.session_state.get("ViewMyCourses_status", False):

    st.divider()

    st.subheader("📚 My Courses")


  

    res = requests.get(
        "http://127.0.0.1:8000/get_my_courses",
        params={
            "t_id": loggedin_Trainer_id
        }
    )



    if res.status_code == 200:

        res_obj_list = res.json()["data"]


        

        if len(res_obj_list) == 0:

            st.info(
                "📭 You have not added any courses yet."
            )


        else:

            

            for course in res_obj_list:

                st.write(
                    "### 📚",
                    course["course_name"]
                )

                st.write(
                    "Description:",
                    course["course_description"]
                )

                st.write(
                    "Duration:",
                    course["course_duration"]
                )
                                                       
                course_status = st.selectbox(
                    "Course Status",
                    ["draft", "published"],
                    format_func=lambda status: {
                        "draft": "📝 Draft — Not available to students",
                        "published": "🚀 Published — Ready for students"
                    }[status],
                    index=["draft", "published"].index(
        course.get("status", "draft")
        if course.get("status", "draft") in ["draft", "published"]
        else "draft"
    ),
    key=f"status_{course['id']}"
                )



               

                cl1, cl2 = st.columns(2)


               

                with cl1:

                    if st.button(
                        "✏️ Edit",
                        key=f"edit_{course['id']}",
                        use_container_width=True
                    ):

                        st.write(
                            "Edit clicked"
                        )

                        st.write(course)


              

                with cl2:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{course['id']}",
                        use_container_width=True
                    ):

                        # st.write(
                        #     "Delete clicked"
                        # )
                        res=requests.delete(f"http://127.0.0.1:8000/deleteCourse/{course['id']}")
                        if res.status_code == 200:
                            res_obj=res.json()
                            res_msg=res_obj["msg"]
                            st.write(res_msg)
                            st.rerun()
                        else:
                            st.write("some eeror occured")    
                        


                st.divider()



    else:

        st.error(
            "❌ Some error occurred while fetching courses."
        )
