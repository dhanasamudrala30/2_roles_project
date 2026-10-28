import html
import requests
import streamlit as st

from helper import login_status_check, role_check

st.set_page_config(
    page_title="Student Dashboard",
    page_icon="🎓",
    layout="wide"
)

login_status_check()
role_check("student")

API_URL = "http://127.0.0.1:8000"

student_name = st.session_state.get("name", "Student")
student_email = st.session_state.get("email", "")
student_id = st.session_state.get("id")

if not student_id:
    st.error("Student ID is missing. Please log in again.")
    st.stop()

for key, default in {
    "student_page": "overview"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


st.markdown("""
<style>
.block-container {
    max-width: 1250px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}
.student-banner {
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(120deg, #25316D, #6554C0);
    color: white;
    margin-bottom: 25px;
}
.student-banner h1 {
    color: white;
    font-size: 31px;
    margin-bottom: 8px;
}
.student-banner p {
    color: #E5E7FF;
    font-size: 15px;
    margin: 0;
}
.section-title {
    font-size: 23px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 5px;
}
.section-caption {
    color: #9CA3AF;
    font-size: 14px;
    margin-bottom: 18px;
}
div[data-testid="stMetric"] {
    padding: 19px;
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 14px;
    background: rgba(128,128,128,0.035);
}
div.stButton > button {
    min-height: 42px;
    border-radius: 10px;
    font-weight: 600;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 15px;
}
.student-label {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #9CA3AF;
    margin-bottom: 5px;
}
.course-description {
    color: #9CA3AF;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


def api_error_message(response):
    try:
        return response.json().get("detail", response.text)
    except (ValueError, AttributeError):
        return response.text


def get_data(endpoint, params=None):
    response = requests.get(
        f"{API_URL}{endpoint}",
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json().get("data", [])


def fetch_courses():
    return get_data("/get_published_courses")


def fetch_enrolled_courses():
    return get_data(
        "/my_enrolled_courses",
        params={"student_id": student_id}
    )


def fetch_student_progress():
    return get_data(
        "/get_lesson_progress",
        params={"student_id": student_id}
    )


def fetch_course_lessons(course_id):
    modules = get_data(
        "/get_modules",
        params={"course_id": course_id}
    )

    lessons = []

    for module in modules:
        module_lessons = get_data(
            "/get_lessons",
            params={"module_id": module["id"]}
        )

        for lesson in module_lessons:
            lesson_copy = dict(lesson)
            lesson_copy["module_title"] = module.get(
                "module_title", "Course Module"
            )
            lessons.append(lesson_copy)

    return sorted(
        lessons,
        key=lambda lesson: (
            lesson.get("module_title", ""),
            lesson.get("lesson_order", 1)
        )
    )


def calculate_progress(lessons, progress_records):
    completed_ids = {
        record["lesson_id"]
        for record in progress_records
        if record.get("is_completed")
    }

    completed = sum(
        1 for lesson in lessons
        if lesson["id"] in completed_ids
    )

    total = len(lessons)
    percentage = round(completed / total * 100) if total else 0

    return completed, total, percentage, completed_ids


def show_enrollment_button(course):
    course_id = course["id"]

    if st.button(
        "🎓 Enroll Now",
        key=f"enroll_{course_id}",
        use_container_width=True,
        type="primary"
    ):
        try:
            response = requests.post(
                f"{API_URL}/enroll_course",
                json={
                    "student_id": student_id,
                    "course_id": course_id
                },
                timeout=10
            )

            if response.status_code in (200, 201):
                st.success("Successfully enrolled!")
                st.rerun()
            elif response.status_code == 409:
                st.info("You are already enrolled in this course.")
            else:
                st.error(
                    f"Enrollment failed: {api_error_message(response)}"
                )

        except requests.RequestException as error:
            st.error(f"Backend connection failed: {error}")


# HEADER
safe_name = html.escape(str(student_name))

st.markdown(
    f"""
    <div class="student-banner">
        <h1>🎓 Student Learning Dashboard</h1>
        <p>Welcome back, {safe_name}! Continue learning and track your progress.</p>
    </div>
    """,
    unsafe_allow_html=True
)


# PROFILE
with st.expander("👤 My Profile", expanded=False):
    profile1, profile2, profile3 = st.columns(3)

    with profile1:
        st.caption("FULL NAME")
        st.write(student_name)

    with profile2:
        st.caption("EMAIL ADDRESS")
        st.write(student_email)

    with profile3:
        st.caption("ROLE")
        st.write("Student")


# LOAD DATA
courses_loaded = False
enrollments_loaded = False
progress_loaded = False

try:
    available_courses = fetch_courses()
    courses_loaded = True
except requests.RequestException as error:
    available_courses = []
    st.error(f"Unable to load published courses: {error}")

try:
    enrolled_courses = fetch_enrolled_courses()
    enrollments_loaded = True
except requests.RequestException as error:
    enrolled_courses = []
    st.error(f"Unable to load your enrollments: {error}")

try:
    progress_records = fetch_student_progress()
    progress_loaded = True
except requests.RequestException as error:
    progress_records = []
    st.warning(f"Learning progress is temporarily unavailable: {error}")


# OVERVIEW METRICS
total_completed = sum(
    1 for record in progress_records
    if record.get("is_completed")
)

st.markdown(
    '<div class="section-title">📊 My Learning Overview</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="section-caption">Your learning activity at a glance.</div>',
    unsafe_allow_html=True
)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric(
        "📚 Available Courses",
        len(available_courses) if courses_loaded else "—"
    )

with metric2:
    st.metric(
        "🎓 My Enrollments",
        len(enrolled_courses) if enrollments_loaded else "—"
    )

with metric3:
    st.metric(
        "✅ Lessons Completed",
        total_completed if progress_loaded else "—"
    )


# NAVIGATION
st.divider()
st.markdown("### 🧭 Learning Centre")

nav1, nav2, nav3 = st.columns(3)

with nav1:
    if st.button(
        "🏠 Overview",
        use_container_width=True,
        type="primary" if st.session_state["student_page"] == "overview" else "secondary"
    ):
        st.session_state["student_page"] = "overview"
        st.rerun()

with nav2:
    if st.button(
        "🔍 Browse Courses",
        use_container_width=True,
        type="primary" if st.session_state["student_page"] == "browse" else "secondary"
    ):
        st.session_state["student_page"] = "browse"
        st.rerun()

with nav3:
    if st.button(
        "📖 My Learning",
        use_container_width=True,
        type="primary" if st.session_state["student_page"] == "my_courses" else "secondary"
    ):
        st.session_state["student_page"] = "my_courses"
        st.rerun()


student_page = st.session_state["student_page"]


# OVERVIEW
if student_page == "overview":
    st.divider()
    st.markdown("### 👋 Welcome to Your Learning Space")

    st.write(
        "Explore published courses, continue your enrolled courses, "
        "and track completed lessons from one place."
    )

    if enrolled_courses:
        st.markdown("#### 📖 Continue Your Learning")

        try:
            for course in enrolled_courses[:3]:
                course_id = course["id"]

                with st.container(border=True):
                    st.markdown(
                        f"### 📘 {course.get('course_name', 'Untitled Course')}"
                    )

                    st.caption(
                        f"⏱️ {course.get('course_duration') or 'Duration not specified'}"
                    )

                    if progress_loaded:
                        lessons = fetch_course_lessons(course_id)

                        completed, total, percentage, _ = calculate_progress(
                            lessons, progress_records
                        )

                        st.progress(
                            percentage / 100,
                            text=f"Course Progress: {percentage}%"
                        )

                        st.caption(
                            f"{completed} of {total} lessons completed"
                            if total
                            else "No lessons have been added to this course yet."
                        )

                    if st.button(
                        "Open My Learning →",
                        key=f"overview_course_{course_id}",
                        use_container_width=True
                    ):
                        st.session_state["student_page"] = "my_courses"
                        st.session_state["selected_learning_course"] = course_id
                        st.rerun()

        except requests.RequestException as error:
            st.warning(f"Unable to load course progress: {error}")
    else:
        st.info(
            "You haven't enrolled in a course yet. "
            "Visit Browse Courses to get started."
        )

    st.markdown("#### ✨ Recommended Next Step")
    st.write(
        "Choose a published course that matches your interests "
        "and begin building your skills."
    )

    if st.button("Explore Available Courses", type="primary"):
        st.session_state["student_page"] = "browse"
        st.rerun()


# BROWSE COURSES
elif student_page == "browse":
    st.divider()
    st.markdown("### 🔍 Explore Courses")
    st.caption("Discover courses and enroll to start learning.")

    search_text = st.text_input(
        "Search courses",
        placeholder="Search by course name or technology..."
    )

    enrolled_ids = {
        course.get("id")
        for course in enrolled_courses
    }

    filtered_courses = [
        course for course in available_courses
        if search_text.lower() in (
            str(course.get("course_name", "")) + " " +
            str(course.get("course_description", "")) + " " +
            str(course.get("technologies", ""))
        ).lower()
    ]

    if not filtered_courses:
        st.info("No matching published courses found.")
    else:
        st.caption(f"{len(filtered_courses)} course(s) found.")

        for course in filtered_courses:
            with st.container(border=True):
                st.markdown(
                    f"### 📘 {course.get('course_name', 'Untitled Course')}"
                )

                st.markdown(
                    f'<div class="course-description">'
                    f'{html.escape(str(course.get("course_description") or "No description available."))}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.write("**Technologies**")
                st.write(
                    course.get("technologies") or "Not specified"
                )

                st.caption(
                    f"⏱️ Duration: {course.get('course_duration') or 'Not specified'}"
                )

                st.success("🚀 Published")

                if course.get("id") in enrolled_ids:
                    st.info("✅ You are already enrolled.")
                else:
                    show_enrollment_button(course)


# MY COURSES / LESSON PROGRESS
elif student_page == "my_courses":
    st.divider()
    st.markdown("### 📖 My Learning")
    st.caption(
        "Open a course, explore its modules, and update your lesson progress."
    )

    if not enrolled_courses:
        st.info(
            "You haven't enrolled in any courses yet. "
            "Browse Courses to find your first course."
        )

    else:
        course_options = {
            f"{course.get('course_name', 'Untitled Course')}": course["id"]
            for course in enrolled_courses
        }

        preferred_course_id = st.session_state.get(
            "selected_learning_course"
        )

        course_names = list(course_options.keys())

        default_index = 0
        if preferred_course_id:
            for index, name in enumerate(course_names):
                if course_options[name] == preferred_course_id:
                    default_index = index
                    break

        selected_course_name = st.selectbox(
            "Select an enrolled course",
            course_names,
            index=default_index,
            key="learning_course_select"
        )

        selected_course_id = course_options[selected_course_name]

        selected_course = next(
            course for course in enrolled_courses
            if course["id"] == selected_course_id
        )

        st.markdown(f"#### 📘 {selected_course_name}")

        st.write(
            selected_course.get("course_description")
            or "Learn through the modules and lessons below."
        )

        st.caption(
            f"Duration: {selected_course.get('course_duration') or 'Not specified'}"
        )

        if not progress_loaded:
            st.warning(
                "Progress could not be loaded. You can still explore lessons, "
                "but completion status may be unavailable."
            )

        try:
            lessons = fetch_course_lessons(selected_course_id)

            completed_ids = set()
            percentage = 0

            if progress_loaded:
                completed, total, percentage, completed_ids = (
                    calculate_progress(lessons, progress_records)
                )

                progress_col1, progress_col2, progress_col3 = st.columns(3)

                with progress_col1:
                    st.metric("Total Lessons", total)

                with progress_col2:
                    st.metric("Completed", completed)

                with progress_col3:
                    st.metric("Course Progress", f"{percentage}%")

                st.progress(
                    percentage / 100,
                    text=f"{percentage}% completed"
                )

            if not lessons:
                st.info(
                    "No lessons are available for this course yet."
                )

            else:
                st.markdown("#### 🧩 Course Lessons")

                for index, lesson in enumerate(lessons, start=1):
                    lesson_id = lesson["id"]
                    is_completed = lesson_id in completed_ids

                    icon = {
                        "video": "🎬",
                        "article": "📄",
                        "resource": "📎"
                    }.get(lesson.get("lesson_type"), "📚")

                    with st.container(border=True):
                        st.markdown(
                            f"**{index:02d}. {icon} "
                            f"{lesson.get('lesson_title', 'Untitled Lesson')}**"
                        )

                        st.caption(
                            f"Module: {lesson.get('module_title', 'Course Module')} "
                            f"· {lesson.get('duration_minutes') or 0} minutes"
                        )

                        if lesson.get("lesson_description"):
                            st.write(lesson["lesson_description"])

                        content_url = lesson.get("content_url")

                        if content_url and content_url.startswith(
                            ("https://", "http://")
                        ):
                            st.markdown(
                                f"[Open lesson content ↗]({content_url})"
                            )

                        if not progress_loaded:
                            st.caption(
                                "Completion status unavailable."
                            )

                        elif is_completed:
                            st.success("✅ Lesson completed")

                            if st.button(
                                "Mark as Incomplete",
                                key=f"incomplete_{lesson_id}",
                                use_container_width=True
                            ):
                                try:
                                    response = requests.post(
                                        f"{API_URL}/update_lesson_progress",
                                        json={
                                            "student_id": student_id,
                                            "lesson_id": lesson_id,
                                            "is_completed": False
                                        },
                                        timeout=10
                                    )

                                    if response.status_code in (200, 201):
                                        st.success("Progress updated.")
                                        st.rerun()
                                    else:
                                        st.error(api_error_message(response))

                                except requests.RequestException as error:
                                    st.error(
                                        f"Unable to update progress: {error}"
                                    )

                        else:
                            if st.button(
                                "✓ Mark as Completed",
                                key=f"complete_{lesson_id}",
                                use_container_width=True,
                                type="primary"
                            ):
                                try:
                                    response = requests.post(
                                        f"{API_URL}/update_lesson_progress",
                                        json={
                                            "student_id": student_id,
                                            "lesson_id": lesson_id,
                                            "is_completed": True
                                        },
                                        timeout=10
                                    )

                                    if response.status_code in (200, 201):
                                        st.success("Lesson marked as completed!")
                                        st.rerun()
                                    else:
                                        st.error(api_error_message(response))

                                except requests.RequestException as error:
                                    st.error(
                                        f"Unable to update progress: {error}"
                                    )

        except requests.RequestException as error:
            st.error(f"Unable to load course lessons: {error}")


