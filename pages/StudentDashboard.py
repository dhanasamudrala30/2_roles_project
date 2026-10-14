import streamlit as st 
import requests

from helper import login_status_check
from helper import role_check

login_status_check()
role_check("student")

# st.title("student dashboard")

student_name = st.session_state["name"]
student_email = st.session_state["email"]
student_id = st.session_state["id"]

st.title("🎓 Student Dashboard")
st.caption(f"Welcome back, {student_name}! 👋")

st.write(f"📧 Email: {student_email}")
st.write("👤 Role: Student")

st.divider()


st.subheader("📊 My Learning Overview")

available_courses_count = 0
my_enrollments_count = 0

try:
    courses_response = requests.get(
        "http://127.0.0.1:8000/get_published_courses",
        timeout=10
    )
    courses_response.raise_for_status()
    available_courses_count = len(
        courses_response.json().get("data", [])
    )
except requests.RequestException:
    st.warning("Unable to load available courses.")

try:
    enrollments_response = requests.get(
        "http://127.0.0.1:8000/my_enrolled_courses",
        params={"student_id": student_id},
        timeout=10
    )
    enrollments_response.raise_for_status()
    my_enrollments_count = len(
        enrollments_response.json().get("data", [])
    )
except requests.RequestException:
    st.warning("Unable to load your enrollments.")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "📚 Available Courses",
        available_courses_count
    )

with col2:
    st.metric(
        "🎓 My Enrollments",
        my_enrollments_count
    )

st.divider()

st.subheader("🚀 Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("📚 Browse Courses", use_container_width=True):
        st.session_state["student_page"] = "browse"
        st.rerun()

with col2:
    if st.button("🎓 My Courses", use_container_width=True):
        st.session_state["student_page"] = "my_courses"
        st.rerun()

student_page = st.session_state.get("student_page", "overview")


if student_page == "browse":
    st.subheader("📚 Available Courses")

    try:
        response = requests.get(
            "http://127.0.0.1:8000/get_published_courses",
            timeout=10
        )
        response.raise_for_status()

        courses = response.json().get("data", [])

        if not courses:
            st.info("No published courses are available yet.")
        else:
            for course in courses:
                with st.container(border=True):
                    st.subheader(f"📘 {course['course_name']}")

                    st.write(
                        course.get("course_description", "")
                    )

                    
                    st.caption(
                        f"Duration: {course.get('course_duration', 'Not specified')}"
                    )

                    st.success("Published")

                    
                    if st.button(
                        "🎓 Enroll Now",
                        key=f"enroll_{course['id']}",
                        use_container_width=True
                    ):
                        try:
                            enrollment_response = requests.post(
                                "http://127.0.0.1:8000/enroll_course",
                                json={
                                    "student_id": student_id,
                                    "course_id": course["id"]
                                },
                                timeout=10
                            )

                            if enrollment_response.status_code == 200:
                                st.success("Successfully enrolled in this course!")

                            elif enrollment_response.status_code == 409:
                                st.warning("You are already enrolled in this course.")

                            else:
                                try:
                                    detail = enrollment_response.json().get(
                                        "detail", "Unable to enroll in this course."
                                    )
                                except ValueError:
                                    detail = enrollment_response.text

                                st.error(f"Enrollment failed: {detail}")

                        except requests.RequestException as error:
                            st.error(f"Could not connect to the backend: {error}")


    except requests.RequestException as error:
        st.error(f"Unable to load courses: {error}")



elif student_page == "my_courses":
    st.subheader("🎓 My Enrolled Courses")

    try:
        response = requests.get(
            "http://127.0.0.1:8000/my_enrolled_courses",
            params={"student_id": student_id},
            timeout=10
        )
        response.raise_for_status()

        courses = response.json().get("data", [])

        if not courses:
            st.info(
                "You haven't enrolled in any courses yet. "
                "Visit Browse Courses to get started!"
            )
        else:
            for course in courses:
                with st.container(border=True):
                    st.subheader(f"📘 {course['course_name']}")

                    st.write(
                        course.get("course_description", "")
                    )

                    st.caption(
                        f"Duration: {course.get('course_duration', 'Not specified')}"
                    )

                    st.success("✅ Enrolled")

    except requests.RequestException as error:
        st.error(f"Unable to load your courses: {error}")
