
import html
import requests
import streamlit as st

from helper import login_status_check, role_check

login_status_check()
role_check("trainer")

API_URL = "http://127.0.0.1:8000"

trainer_name = st.session_state["name"]
trainer_email = st.session_state["email"]
trainer_role = st.session_state["role"]
trainer_id = st.session_state["id"]

st.set_page_config(
    page_title="Trainer Dashboard",
    page_icon="👨‍🏫",
    layout="wide"
)

for key, default in {
    "addCourse_status": False,
    "ViewMyCourses_status": False,
    "manage_modules_status": False,
    "show_module_form": False,
    "module_course_id": None,
    "delete_module_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
.block-container {
    max-width: 1250px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}
.dashboard-banner {
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(120deg, #25316D 0%, #6554C0 100%);
    color: #FFFFFF;
    margin-bottom: 26px;
}
.dashboard-banner h1 {
    color: #FFFFFF;
    font-size: 32px;
    margin-bottom: 8px;
}
.dashboard-banner p {
    color: #E4E7FF;
    margin: 0;
    font-size: 15px;
}
.section-heading {
    font-size: 24px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 5px;
}
.section-caption {
    color: #9CA3AF;
    font-size: 14px;
    margin-bottom: 20px;
}
div[data-testid="stMetric"] {
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.28);
    background: rgba(128,128,128,0.04);
}
div.stButton > button,
div.stFormSubmitButton > button {
    border-radius: 10px;
    min-height: 43px;
    font-weight: 600;
}
div[data-testid="stForm"] {
    border-radius: 14px;
    padding: 20px;
    border: 1px solid rgba(128,128,128,0.25);
}
.course-title {
    font-size: 21px;
    font-weight: 700;
    margin-bottom: 12px;
}
.course-description {
    line-height: 1.65;
    color: #AEB7C5;
}
.module-empty-state {
    text-align: center;
    border: 1px dashed #64748B;
    border-radius: 15px;
    padding: 30px 18px;
    margin-top: 10px;
}
.module-empty-state h3 {
    margin-bottom: 8px;
}
.module-empty-state p {
    color: #9CA3AF;
    margin-bottom: 0;
}
.info-label {
    font-size: 12px;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)


def api_error_message(response):
    try:
        return response.json().get("detail", response.text)
    except (ValueError, AttributeError):
        return response.text


def fetch_courses():
    response = requests.get(
        f"{API_URL}/get_my_courses",
        params={"t_id": trainer_id},
        timeout=10
    )
    response.raise_for_status()
    return response.json().get("data", [])


def fetch_modules(course_id):
    response = requests.get(
        f"{API_URL}/get_modules",
        params={"course_id": course_id},
        timeout=10
    )
    response.raise_for_status()
    return response.json().get("data", [])


def clear_module_form():
    st.session_state["show_module_form"] = False
    st.session_state["module_course_id"] = None


# HEADER
safe_name = html.escape(str(trainer_name))

st.markdown(
    f"""
    <div class="dashboard-banner">
        <h1>👨‍🏫 Trainer Dashboard</h1>
        <p>Welcome back, {safe_name}! Manage your courses, organize
        learning content, and help students grow.</p>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("👤 Trainer Profile", expanded=False):
    profile1, profile2, profile3 = st.columns(3)

    with profile1:
        st.caption("FULL NAME")
        st.write(trainer_name)

    with profile2:
        st.caption("EMAIL ADDRESS")
        st.write(trainer_email)

    with profile3:
        st.caption("ROLE")
        st.write(trainer_role)


# LOAD COURSES AND METRICS
st.markdown(
    '<div class="section-heading">📊 Dashboard Overview</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="section-caption">A quick overview of your training courses.</div>',
    unsafe_allow_html=True
)

try:
    courses = fetch_courses()
    courses_loaded = True
except requests.RequestException as error:
    courses = []
    courses_loaded = False
    st.error(f"Unable to load courses. Check your backend connection. ({error})")

total_courses = len(courses)
published_courses = sum(
    1 for course in courses
    if course.get("status") == "published"
)
draft_courses = total_courses - published_courses

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("📚 Total Courses", total_courses if courses_loaded else "—")

with metric2:
    st.metric("🚀 Published Courses", published_courses if courses_loaded else "—")

with metric3:
    st.metric("📝 Draft Courses", draft_courses if courses_loaded else "—")


# MAIN ACTIONS
st.divider()

st.markdown(
    '<div class="section-heading">🛠️ Course Management</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="section-caption">Choose an action to manage your learning content.</div>',
    unsafe_allow_html=True
)

action1, action2, action3 = st.columns(3)

with action1:
    if st.button("➕ Add Course", use_container_width=True):
        st.session_state["addCourse_status"] = True
        st.session_state["ViewMyCourses_status"] = False
        st.session_state["manage_modules_status"] = False
        clear_module_form()
        st.rerun()

with action2:
    if st.button("📚 View My Courses", use_container_width=True):
        st.session_state["ViewMyCourses_status"] = True
        st.session_state["addCourse_status"] = False
        st.session_state["manage_modules_status"] = False
        clear_module_form()
        st.rerun()

with action3:
    if st.button("🧩 Manage Modules", use_container_width=True):
        st.session_state["manage_modules_status"] = True
        st.session_state["addCourse_status"] = False
        st.session_state["ViewMyCourses_status"] = False
        clear_module_form()
        st.rerun()


# ADD COURSE
if st.session_state["addCourse_status"]:
    st.divider()
    st.subheader("➕ Create a New Course")
    st.caption("Provide the course information below.")

    with st.form("addCourseForm"):
        course_name = st.text_input(
            "Course Name",
            placeholder="Example: Java Full Stack Development"
        )

        course_technologies = st.text_input(
            "Technologies Used",
            placeholder="Example: Java, Spring Boot, React.js, MySQL"
        )

        description = st.text_area(
            "Course Description",
            placeholder="Describe the course objectives and learning outcomes.",
            height=120
        )

        duration = st.text_input(
            "Course Duration",
            placeholder="Example: 16 Weeks"
        )

        course_status = st.selectbox(
            "Course Status",
            ["draft", "published"],
            format_func=lambda status: {
                "draft": "📝 Draft — Not available to students",
                "published": "🚀 Published — Ready for students"
            }[status]
        )

        save_col, cancel_col = st.columns(2)

        with save_col:
            submit_course = st.form_submit_button(
                "➕ Add Course",
                use_container_width=True
            )

        with cancel_col:
            cancel_course = st.form_submit_button(
                "✖ Cancel",
                use_container_width=True
            )

    if cancel_course:
        st.session_state["addCourse_status"] = False
        st.rerun()

    if submit_course:
        if not all([
            course_name.strip(),
            course_technologies.strip(),
            description.strip(),
            duration.strip()
        ]):
            st.error("Please complete all course fields.")
        else:
            payload = {
                "trainer_id": trainer_id,
                "course_name": course_name.strip(),
                "course_description": description.strip(),
                "course_duration": duration.strip(),
                "status": course_status,
                "technologies": course_technologies.strip()
            }

            try:
                response = requests.post(
                    f"{API_URL}/add_course",
                    json=payload,
                    timeout=10
                )

                if response.status_code in (200, 201):
                    st.success("Course added successfully!")
                    st.session_state["addCourse_status"] = False
                    st.rerun()
                else:
                    st.error("Unable to create the course.")
                    st.code(api_error_message(response))

            except requests.RequestException as error:
                st.error(f"Unable to connect to the backend: {error}")


# VIEW MY COURSES
if st.session_state["ViewMyCourses_status"]:
    st.divider()
    st.subheader("📚 My Courses")
    st.caption("Review your course details and manage course records.")

    if not courses_loaded:
        st.warning("Courses are unavailable until the backend connection is restored.")
    elif not courses:
        st.markdown("""
        <div class="module-empty-state">
            <h3>📚 No courses yet</h3>
            <p>Create your first course to start building your learning content.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for course in courses:
            course_id = course["id"]

            with st.container(border=True):
                st.markdown(
                    f"### 📘 {course.get('course_name', 'Untitled Course')}"
                )

                status = course.get("status", "draft")

                if status == "published":
                    st.success("🚀 Published")
                else:
                    st.info("📝 Draft")

                st.markdown("**Technology Stack**")
                st.write(course.get("technologies") or "Not specified")

                st.markdown("**About this Course**")
                st.write(course.get("course_description") or "No description provided.")

                st.caption(
                    f"⏱️ Duration: {course.get('course_duration') or 'Not specified'}"
                )

                confirm_key = f"confirm_delete_course_{course_id}"

                if st.button(
                    "🗑️ Delete Course",
                    key=f"delete_course_{course_id}",
                    use_container_width=True
                ):
                    st.session_state[confirm_key] = True

                if st.session_state.get(confirm_key, False):
                    st.warning(
                        "Deleting a course may also delete its modules, lessons, "
                        "and enrollments depending on your database relationships."
                    )

                    yes_col, no_col = st.columns(2)

                    with yes_col:
                        if st.button(
                            "Confirm Delete",
                            key=f"confirm_course_{course_id}",
                            use_container_width=True
                        ):
                            try:
                                delete_response = requests.delete(
                                    f"{API_URL}/deleteCourse/{course_id}",
                                    timeout=10
                                )

                                if delete_response.status_code == 200:
                                    st.session_state.pop(confirm_key, None)
                                    st.success("Course deleted successfully.")
                                    st.rerun()
                                else:
                                    st.error(api_error_message(delete_response))

                            except requests.RequestException as error:
                                st.error(f"Unable to delete course: {error}")

                    with no_col:
                        if st.button(
                            "Cancel",
                            key=f"cancel_course_{course_id}",
                            use_container_width=True
                        ):
                            st.session_state.pop(confirm_key, None)
                            st.rerun()


# MANAGE MODULES
if st.session_state["manage_modules_status"]:
    st.divider()
    st.subheader("🧩 Manage Course Modules")
    st.caption("Select a course to create, view, and manage its modules.")

    if not courses_loaded:
        st.warning("Unable to load courses. Check the backend.")
    elif not courses:
        st.info("Create a course before adding modules.")
    else:
        course_options = {
            f"{course['course_name']}": course["id"]
            for course in courses
        }

        selected_course_name = st.selectbox(
            "Select Course",
            list(course_options.keys()),
            key="module_course_select"
        )

        selected_course_id = course_options[selected_course_name]

        create_module_col, refresh_col = st.columns(2)

        with create_module_col:
            if st.button(
                "➕ Create New Module",
                use_container_width=True
            ):
                st.session_state["show_module_form"] = True
                st.session_state["module_course_id"] = selected_course_id
                st.rerun()

        with refresh_col:
            if st.button(
                "🔄 Refresh Modules",
                use_container_width=True
            ):
                st.rerun()

        if (
            st.session_state["show_module_form"]
            and st.session_state["module_course_id"] != selected_course_id
        ):
            clear_module_form()

        if (
            st.session_state["show_module_form"]
            and st.session_state["module_course_id"] == selected_course_id
        ):
            st.markdown("### 📝 Create Module")

            with st.form("add_module_form"):
                module_title = st.text_input(
                    "Module Title",
                    placeholder="Example: Java Fundamentals and OOP"
                )

                module_description = st.text_area(
                    "Module Description",
                    placeholder="Describe what students will learn in this module.",
                    height=100
                )

                module_order = st.number_input(
                    "Module Order",
                    min_value=1,
                    value=1,
                    step=1
                )

                module_save_col, module_cancel_col = st.columns(2)

                with module_save_col:
                    submit_module = st.form_submit_button(
                        "💾 Save Module",
                        use_container_width=True
                    )

                with module_cancel_col:
                    cancel_module = st.form_submit_button(
                        "✖ Cancel",
                        use_container_width=True
                    )

            if cancel_module:
                clear_module_form()
                st.rerun()

            if submit_module:
                if not module_title.strip():
                    st.error("Please enter a module title.")
                else:
                    payload = {
                        "course_id": selected_course_id,
                        "module_title": module_title.strip(),
                        "module_description": module_description.strip(),
                        "module_order": int(module_order)
                    }

                    try:
                        module_response = requests.post(
                            f"{API_URL}/add_module",
                            json=payload,
                            timeout=10
                        )

                        if module_response.status_code in (200, 201):
                            st.success("Module created successfully!")
                            clear_module_form()
                            st.rerun()
                        else:
                            st.error("Unable to create module.")
                            st.code(api_error_message(module_response))

                    except requests.RequestException as error:
                        st.error(f"Backend connection failed: {error}")

        st.divider()
        st.markdown("### 📖 Existing Modules")
        st.caption("Modules are listed in their configured learning order.")

        try:
            modules = fetch_modules(selected_course_id)

            if not modules:
                st.markdown("""
                <div class="module-empty-state">
                    <h3>📚 No modules yet</h3>
                    <p>Create your first module to organize this course into lessons.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for module in modules:
                    module_id = module["id"]
                    module_confirm_key = f"confirm_delete_module_{module_id}"

                    with st.container(border=True):
                        st.markdown(
                            f"### 📖 Module {module.get('module_order', 1)}: "
                            f"{module.get('module_title', 'Untitled Module')}"
                        )

                        st.write(
                            module.get("module_description")
                            or "No module description provided."
                        )

                        st.caption(
                            f"Module ID: {module_id}"
                        )

                        if st.button(
                            "🗑️ Delete Module",
                            key=f"delete_module_{module_id}",
                            use_container_width=True
                        ):
                            st.session_state["delete_module_id"] = module_id
                            st.rerun()

                        if st.session_state.get("delete_module_id") == module_id:
                            st.warning(
                                "Are you sure you want to delete this module? "
                                "Its lessons may also be deleted."
                            )

                            confirm_col, cancel_col = st.columns(2)

                            with confirm_col:
                                if st.button(
                                    "Confirm Delete",
                                    key=f"confirm_module_{module_id}",
                                    use_container_width=True
                                ):
                                    try:
                                        delete_response = requests.delete(
                                            f"{API_URL}/delete_module/{module_id}",
                                            timeout=10
                                        )

                                        if delete_response.status_code == 200:
                                            st.session_state.pop(
                                                "delete_module_id", None
                                            )
                                            st.success("Module deleted successfully.")
                                            st.rerun()
                                        else:
                                            st.error(api_error_message(delete_response))

                                    except requests.RequestException as error:
                                        st.error(f"Module deletion failed: {error}")

                            with cancel_col:
                                if st.button(
                                    "Cancel",
                                    key=f"cancel_module_{module_id}",
                                    use_container_width=True
                                ):
                                    st.session_state.pop("delete_module_id", None)
                                    st.rerun()
        except requests.RequestException as error:
            st.error(
                "Unable to load modules. Confirm that GET /get_modules exists "
                "in main.py and that your FastAPI server is running."
            )
            st.caption(str(error))


# MANAGE LESSONS
st.markdown("""
<style>
.lesson-header {
    padding: 24px 26px;
    border-radius: 16px;
    background: linear-gradient(120deg, #25316D, #6554C0);
    color: white;
    margin: 20px 0 24px 0;
}
.lesson-header h2 {
    color: white;
    margin: 0 0 7px 0;
    font-size: 27px;
}
.lesson-header p {
    color: #E5E7FF;
    margin: 0;
    font-size: 14px;
}
.lesson-panel {
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 16px;
    padding: 22px;
    margin: 12px 0;
    background: rgba(128,128,128,0.035);
}
.lesson-label {
    color: #9CA3AF;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.lesson-item {
    padding: 15px;
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 12px;
    margin-bottom: 10px;
    background: rgba(128,128,128,0.035);
}
.lesson-item-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 7px;
}
.lesson-item-meta {
    color: #9CA3AF;
    font-size: 13px;
}
.lesson-empty {
    padding: 28px 16px;
    border: 1px dashed #64748B;
    border-radius: 14px;
    text-align: center;
    margin-top: 12px;
}
</style>

<div class="lesson-header">
    <h2>📚 Lesson Studio</h2>
    <p>Create, organize, and manage the learning content inside your course modules.</p>
</div>
""", unsafe_allow_html=True)

if not courses_loaded:
    st.error("Unable to load courses. Please check your backend connection.")

elif not courses:
    st.info("Create a course first, then add modules and lessons.")

else:
    course_options = {
        f"{course.get('course_name', 'Untitled Course')}": course["id"]
        for course in courses
    }

    st.markdown("#### 🎯 Choose Your Learning Path")

    selected_course_name = st.selectbox(
        "Course",
        list(course_options.keys()),
        key="lesson_course",
        label_visibility="collapsed"
    )

    selected_course_id = course_options[selected_course_name]

    selected_course = next(
        course for course in courses
        if course["id"] == selected_course_id
    )

    course_col1, course_col2 = st.columns([3, 1])

    with course_col1:
        st.caption("SELECTED COURSE")
        st.markdown(f"### 📘 {selected_course_name}")
        st.write(
            selected_course.get("course_description")
            or "Build your course by adding structured lessons."
        )

    with course_col2:
        st.caption("COURSE DURATION")
        st.markdown(
            f"### ⏱️ {selected_course.get('course_duration') or 'Not specified'}"
        )
        st.caption(
            f"Status: {selected_course.get('status', 'draft').title()}"
        )

    try:
        modules = fetch_modules(selected_course_id)

        if not modules:
            st.markdown("""
            <div class="lesson-empty">
                <h3>🧩 No modules available</h3>
                <p>Create a module in Manage Modules before adding lessons.</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            module_options = {
                f"Module {module.get('module_order', 1)} · "
                f"{module.get('module_title', 'Untitled Module')}":
                module["id"]
                for module in modules
            }

            st.divider()
            st.markdown("#### 🧩 Select Module")

            selected_module_name = st.selectbox(
                "Module",
                list(module_options.keys()),
                key="lesson_module",
                label_visibility="collapsed"
            )

            selected_module_id = module_options[selected_module_name]

            selected_module = next(
                module for module in modules
                if module["id"] == selected_module_id
            )

            st.markdown(
                f"""
                <div class="lesson-panel">
                    <div class="lesson-label">CURRENT MODULE</div>
                    <div style="font-size:21px;font-weight:700;">
                        📖 {html.escape(selected_module.get('module_title', 'Untitled Module'))}
                    </div>
                    <div style="margin-top:8px;color:#9CA3AF;">
                        {html.escape(selected_module.get('module_description') or 'Add lessons to build this module.')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("#### ✨ Create a Lesson")
            st.caption(
                "Add a video, article, or learning resource to the selected module."
            )

            with st.container(border=True):
                with st.form("add_lesson_form", clear_on_submit=True):
                    lesson_title = st.text_input(
                        "Lesson Title",
                        placeholder="e.g. Introduction to Java"
                    )

                    lesson_description = st.text_area(
                        "Lesson Description",
                        placeholder="Explain the key concepts covered in this lesson.",
                        height=100
                    )

                    lesson_col1, lesson_col2 = st.columns(2)

                    with lesson_col1:
                        lesson_type = st.selectbox(
                            "Content Type",
                            ["video", "article", "resource"],
                            format_func=lambda value: {
                                "video": "🎬 Video Lesson",
                                "article": "📄 Article",
                                "resource": "📎 Learning Resource"
                            }[value]
                        )

                    with lesson_col2:
                        duration_minutes = st.number_input(
                            "Duration (minutes)",
                            min_value=1,
                            max_value=1440,
                            value=10,
                            step=5
                        )

                    content_url = st.text_input(
                        "Content URL",
                        placeholder="https://example.com/lesson"
                    )

                    lesson_order = st.number_input(
                        "Lesson Sequence",
                        min_value=1,
                        value=1,
                        step=1,
                        help="Controls the order in which lessons appear."
                    )

                    submitted = st.form_submit_button(
                        "＋ Create Lesson",
                        use_container_width=True,
                        type="primary"
                    )

                if submitted:
                    if not lesson_title.strip():
                        st.warning("Please enter a lesson title.")

                    elif content_url.strip() and not content_url.strip().startswith(
                        ("https://", "http://")
                    ):
                        st.warning(
                            "Enter a valid URL starting with http:// or https://."
                        )

                    else:
                        payload = {
                            "module_id": selected_module_id,
                            "lesson_title": lesson_title.strip(),
                            "lesson_description": lesson_description.strip(),
                            "lesson_type": lesson_type,
                            "content_url": content_url.strip(),
                            "lesson_order": int(lesson_order),
                            "duration_minutes": int(duration_minutes)
                        }

                        try:
                            response = requests.post(
                                f"{API_URL}/add_lesson",
                                json=payload,
                                timeout=15
                            )

                            if response.status_code in (200, 201):
                                st.success("Lesson created successfully!")
                                st.rerun()
                            else:
                                st.error("Unable to create the lesson.")
                                st.code(api_error_message(response))

                        except requests.RequestException as error:
                            st.error(f"Backend connection failed: {error}")

            st.divider()
            st.markdown("#### 📚 Lesson Library")

            try:
                lessons_response = requests.get(
                    f"{API_URL}/get_lessons",
                    params={"module_id": selected_module_id},
                    timeout=10
                )
                lessons_response.raise_for_status()
                lessons = lessons_response.json().get("data", [])

                lesson_count_col, duration_col = st.columns(2)

                with lesson_count_col:
                    st.metric("Total Lessons", len(lessons))

                total_duration = sum(
                    int(lesson.get("duration_minutes") or 0)
                    for lesson in lessons
                )

                with duration_col:
                    st.metric("Total Learning Time", f"{total_duration} min")

                if lessons:
                    for index, lesson in enumerate(lessons, start=1):
                        lesson_type_value = lesson.get(
                            "lesson_type", "resource"
                        )

                        type_display = {
                            "video": "🎬 Video",
                            "article": "📄 Article",
                            "resource": "📎 Resource"
                        }.get(lesson_type_value, "📚 Lesson")

                        with st.container(border=True):
                            title_col, type_col = st.columns([3, 1])

                            with title_col:
                                st.markdown(
                                    f"**{index:02d} · "
                                    f"{lesson.get('lesson_title', 'Untitled Lesson')}**"
                                )

                            with type_col:
                                st.caption(type_display)

                            description_text = lesson.get(
                                "lesson_description"
                            )

                            if description_text:
                                st.write(description_text)

                            meta_col1, meta_col2 = st.columns(2)

                            with meta_col1:
                                st.caption(
                                    f"⏱️ {lesson.get('duration_minutes') or 0} minutes"
                                )

                            with meta_col2:
                                st.caption(
                                    f"Sequence: {lesson.get('lesson_order', index)}"
                                )

                            lesson_url = lesson.get("content_url")

                            if lesson_url and lesson_url.startswith(
                                ("https://", "http://")
                            ):
                                st.markdown(
                                    f"[Open lesson content ↗]({lesson_url})"
                                )
                else:
                    st.markdown("""
                    <div class="lesson-empty">
                        <h3>📖 Your lesson library is empty</h3>
                        <p>Create your first lesson using the form above.</p>
                    </div>
                    """, unsafe_allow_html=True)

            except requests.RequestException as error:
                st.error("Unable to load lessons from the backend.")
                st.caption(str(error))

    except requests.RequestException as error:
        st.error("Unable to load modules for this course.")
        st.caption(str(error))
