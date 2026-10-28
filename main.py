# uvicorn
# fastapi

SUPABASE_URL="https://qqjktgwwzsxxctbhuczv.supabase.co"
SUPABASE_KEY="sb_publishable_TNvD8HGn8lC8CGpyuHkU5A_Y3XXcYQR"

# pip install supabase
# pip install uvicorn fastapi
# python -m pip install uvicorn fastapi
# py -m pip install uvicorn fastapi

from fastapi import FastAPI # importing FastAPI class
from supabase import create_client
import traceback
from fastapi import HTTPException
from fastapi import FastAPI, HTTPException
fastapi_obj=FastAPI() # creating fastapi object
supabase_obj=create_client(SUPABASE_URL,SUPABASE_KEY)
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ModuleCreate(BaseModel):
    course_id: str
    module_title: str = Field(min_length=1, max_length=150)
    module_description: str = ""
    module_order: int = Field(default=1, ge=1)


class LessonCreate(BaseModel):
    module_id: str
    lesson_title: str = Field(min_length=1, max_length=200)
    lesson_description: str = ""
    lesson_type: str = Field(default="video")
    content_url: str = ""
    lesson_order: int = Field(default=1, ge=1)
    duration_minutes: int = Field(default=10, ge=1)

class LessonProgressCreate(BaseModel):
    student_id: str
    lesson_id: str
    is_completed: bool = True



@fastapi_obj.get("/get_lesson_progress")
def get_lesson_progress(student_id: str):
    try:
        result = (
            supabase_obj.table("lesson_progress")
            .select("*")
            .eq("student_id", student_id)
            .execute()
        )

        return {
            "msg": "Lesson progress fetched successfully.",
            "data": result.data
        }

    except Exception as error:
        print("GET LESSON PROGRESS ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch lesson progress."
        )


@fastapi_obj.post("/update_lesson_progress")
def update_lesson_progress(progress: LessonProgressCreate):
    try:
        lesson_response = (
            supabase_obj.table("lessons")
            .select("id")
            .eq("id", progress.lesson_id)
            .execute()
        )

        if not lesson_response.data:
            raise HTTPException(
                status_code=404,
                detail="Lesson not found."
            )

        existing_response = (
            supabase_obj.table("lesson_progress")
            .select("id")
            .eq("student_id", progress.student_id)
            .eq("lesson_id", progress.lesson_id)
            .execute()
        )

        progress_data = {
            "student_id": progress.student_id,
            "lesson_id": progress.lesson_id,
            "is_completed": progress.is_completed,
            "completed_at": (
                datetime.now(timezone.utc).isoformat()
                if progress.is_completed
                else None
            )
        }

        if existing_response.data:
            result = (
                supabase_obj.table("lesson_progress")
                .update(progress_data)
                .eq("id", existing_response.data[0]["id"])
                .execute()
            )
        else:
            result = (
                supabase_obj.table("lesson_progress")
                .insert(progress_data)
                .execute()
            )

        return {
            "msg": "Lesson progress updated successfully.",
            "data": result.data
        }

    except HTTPException:
        raise
    except Exception as error:
        print("LESSON PROGRESS ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to update lesson progress."
        )


# ---------------------------------------Lessons--------------------

@fastapi_obj.get("/get_lessons")
def get_lessons(module_id: str):
    try:
        result = (
            supabase_obj.table("lessons")
            .select("*")
            .eq("module_id", module_id)
            .order("lesson_order")
            .execute()
        )

        return {
            "msg": "Lessons fetched successfully.",
            "data": result.data
        }

    except Exception as error:
        print("GET LESSONS ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch lessons."
        )

@fastapi_obj.post("/add_lesson")
def add_lesson(lesson: LessonCreate):
    try:
        if lesson.lesson_type not in ["video", "article", "resource"]:
            raise HTTPException(
                status_code=400,
                detail="Lesson type must be video, article, or resource."
            )

        module_response = (
            supabase_obj.table("modules")
            .select("id")
            .eq("id", lesson.module_id)
            .execute()
        )

        if not module_response.data:
            raise HTTPException(
                status_code=404,
                detail="Module not found."
            )

        result = supabase_obj.table("lessons").insert({
            "module_id": lesson.module_id,
            "lesson_title": lesson.lesson_title.strip(),
            "lesson_description": lesson.lesson_description.strip(),
            "lesson_type": lesson.lesson_type,
            "content_url": lesson.content_url.strip(),
            "lesson_order": lesson.lesson_order,
            "duration_minutes": lesson.duration_minutes
        }).execute()

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Lesson could not be created."
            )

        return {
            "msg": "Lesson created successfully.",
            "data": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as error:
        print("ADD LESSON ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to create lesson."
        )



# -------------------- COURSES --------------------

@fastapi_obj.get("/get_my_courses")
def get_my_courses_fun(t_id: str):
    try:
        response = (
            supabase_obj.table("courses")
            .select("*")
            .eq("trainer_id", t_id)
            .execute()
        )

        return {
            "msg": "Courses retrieved successfully",
            "data": response.data
        }

    except Exception as error:
        print("GET COURSES ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve courses."
        )


@fastapi_obj.post("/add_course")
def add_course_fun(new_course: dict):
    try:
        response = (
            supabase_obj.table("courses")
            .insert(new_course)
            .execute()
        )

        return {
            "msg": "Course added successfully",
            "data": response.data
        }

    except Exception as error:
        print("ADD COURSE ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to add course. Check the submitted fields."
        )


@fastapi_obj.delete("/deleteCourse/{c_id}")
def course_delete(c_id: str):
    try:
        response = (
            supabase_obj.table("courses")
            .delete()
            .eq("id", c_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Course not found."
            )

        return {
            "msg": (
                f"{response.data[0]['course_name']} "
                "course deleted successfully"
            )
        }

    except HTTPException:
        raise
    except Exception as error:
        print("DELETE COURSE ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to delete course."
        )


@fastapi_obj.get("/get_published_courses")
def get_published_courses():
    try:
        response = (
            supabase_obj.table("courses")
            .select("*")
            .eq("status", "published")
            .execute()
        )

        return {
            "msg": "Published courses retrieved successfully",
            "data": response.data
        }

    except Exception as error:
        print("PUBLISHED COURSES ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve published courses."
        )


# -------------------- MODULES --------------------

@fastapi_obj.post("/add_module")
def add_module(module: ModuleCreate):
    try:
        # Verify that the selected course exists.
        course_response = (
            supabase_obj.table("courses")
            .select("id")
            .eq("id", module.course_id)
            .execute()
        )

        if not course_response.data:
            raise HTTPException(
                status_code=404,
                detail="Course not found."
            )

        response = (
            supabase_obj.table("modules")
            .insert({
                "course_id": module.course_id,
                "module_title": module.module_title.strip(),
                "module_description": module.module_description.strip(),
                "module_order": module.module_order
            })
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Module could not be created."
            )

        return {
            "msg": "Module created successfully",
            "data": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as error:
        print("ADD MODULE ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to create module."
        )


@fastapi_obj.get("/get_modules")
def get_modules(course_id: str):
    try:
        response = (
            supabase_obj.table("modules")
            .select("*")
            .eq("course_id", course_id)
            .order("module_order")
            .execute()
        )

        return {
            "msg": "Modules retrieved successfully",
            "data": response.data
        }

    except Exception as error:
        print("GET MODULES ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve modules."
        )


@fastapi_obj.delete("/delete_module/{module_id}")
def delete_module(module_id: str):
    try:
        response = (
            supabase_obj.table("modules")
            .delete()
            .eq("id", module_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Module not found."
            )

        return {
            "msg": "Module deleted successfully",
            "data": response.data
        }

    except HTTPException:
        raise
    except Exception as error:
        print("DELETE MODULE ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to delete module."
        )


# -------------------- STUDENT ENROLLMENTS --------------------

@fastapi_obj.post("/enroll_course")
def enroll_course(enrollment: dict):
    student_id = enrollment.get("student_id")
    course_id = enrollment.get("course_id")

    if not student_id or not course_id:
        raise HTTPException(
            status_code=400,
            detail="Student ID and Course ID are required."
        )

    try:
        course_response = (
            supabase_obj.table("courses")
            .select("id, course_name")
            .eq("id", course_id)
            .eq("status", "published")
            .execute()
        )

        if not course_response.data:
            raise HTTPException(
                status_code=404,
                detail="Published course not found."
            )

        existing = (
            supabase_obj.table("enrollments")
            .select("id")
            .eq("student_id", student_id)
            .eq("course_id", course_id)
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=409,
                detail="You are already enrolled in this course."
            )

        response = (
            supabase_obj.table("enrollments")
            .insert({
                "student_id": student_id,
                "course_id": course_id,
                "status": "active"
            })
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Enrollment was not saved."
            )

        return {
            "msg": "Course enrollment successful",
            "data": response.data[0]
        }

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Enrollment failed."
        )


@fastapi_obj.get("/my_enrolled_courses")
def get_my_enrolled_courses(student_id: str):
    try:
        enrollment_response = (
            supabase_obj.table("enrollments")
            .select("course_id, status, enrolled_at")
            .eq("student_id", student_id)
            .eq("status", "active")
            .execute()
        )

        enrollments = enrollment_response.data

        if not enrollments:
            return {
                "msg": "No enrolled courses found",
                "data": []
            }

        course_ids = [
            enrollment["course_id"]
            for enrollment in enrollments
        ]

        courses_response = (
            supabase_obj.table("courses")
            .select("*")
            .in_("id", course_ids)
            .execute()
        )

        return {
            "msg": "Enrolled courses retrieved successfully",
            "data": courses_response.data
        }

    except Exception as error:
        print("MY COURSES ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve enrolled courses."
        )


@fastapi_obj.get("/trainer_course_enrollments")
def trainer_course_enrollments_fun(t_id: str):
    try:
        courses_response = (
            supabase_obj.table("courses")
            .select("id, course_name")
            .eq("trainer_id", t_id)
            .execute()
        )

        courses = courses_response.data or []

        if not courses:
            return {
                "msg": "Course enrollments retrieved successfully",
                "data": []
            }

        course_ids = [course["id"] for course in courses]

        enrollment_response = (
            supabase_obj.table("enrollments")
            .select("course_id, student_id")
            .in_("course_id", course_ids)
            .eq("status", "active")
            .execute()
        )

        enrollments = enrollment_response.data or []

        enrollment_counts = {}

        for enrollment in enrollments:
            course_id = enrollment["course_id"]
            enrollment_counts.setdefault(course_id, set()).add(
                enrollment["student_id"]
            )

        result = []

        for course in courses:
            course_id = course["id"]
            result.append({
                "course_name": course["course_name"],
                "total_students": len(enrollment_counts.get(course_id, set()))
            })

        return {
            "msg": "Course enrollments retrieved successfully",
            "data": result
        }

    except Exception as error:
        print("COURSE ENROLLMENTS ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve course enrollments."
        )


# -------------------- AUTHENTICATION --------------------

@fastapi_obj.post("/login")
def login_validation(login_cred_details: dict):
    try:
        incoming_email = login_cred_details["email"]
        incoming_password = login_cred_details["password"]
        incoming_role = login_cred_details["role"]

        response = (
            supabase_obj.table("users")
            .select("id, name, email, role")
            .eq("email", incoming_email)
            .eq("password", incoming_password)
            .eq("role", incoming_role)
            .execute()
        )

        if not response.data:
            return {
                "msg": "Invalid credentials",
                "status": False
            }

        return {
            "msg": "Login successful",
            "status": True,
            "loggedIn_user": response.data[0]
        }

    except KeyError:
        raise HTTPException(
            status_code=400,
            detail="Email, password, and role are required."
        )
    except Exception as error:
        print("LOGIN ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to process login."
        )


@fastapi_obj.post("/register")
def user_registration(new_user: dict):
    try:
        response = (
            supabase_obj.table("users")
            .insert(new_user)
            .execute()
        )

        return {
            "msg": "Registration successful",
            "data": response.data
        }

    except Exception as error:
        print("REGISTRATION ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to register user."
        )


@fastapi_obj.get("/trainer_analytics")
def trainer_analytics_fun(t_id: str):
    try:
        courses_response = (
            supabase_obj.table("courses")
            .select("id")
            .eq("trainer_id", t_id)
            .execute()
        )

        courses = courses_response.data or []
        course_ids = [course["id"] for course in courses]

        if not course_ids:
            return {
                "msg": "Analytics retrieved successfully",
                "data": {
                    "total_courses": 0,
                    "total_students": 0,
                    "total_lessons": 0,
                    "completed_lessons": 0,
                    "pending_lessons": 0,
                    "completion_rate": 0
                }
            }

        modules_response = (
            supabase_obj.table("modules")
            .select("id")
            .in_("course_id", course_ids)
            .execute()
        )

        modules = modules_response.data or []
        module_ids = [module["id"] for module in modules]

        lesson_ids = []

        if module_ids:
            lessons_response = (
                supabase_obj.table("lessons")
                .select("id")
                .in_("module_id", module_ids)
                .execute()
            )

            lessons = lessons_response.data or []
            lesson_ids = [lesson["id"] for lesson in lessons]

        enrollments_response = (
            supabase_obj.table("enrollments")
            .select("student_id, course_id")
            .in_("course_id", course_ids)
            .eq("status", "active")
            .execute()
        )

        enrollments = enrollments_response.data or []

        total_students = len({
            enrollment["student_id"]
            for enrollment in enrollments
        })

        total_lessons = len(lesson_ids)
        completed_lessons = 0
        pending_lessons = 0

        if lesson_ids:
            progress_response = (
                supabase_obj.table("lesson_progress")
                .select("lesson_id, is_completed")
                .in_("lesson_id", lesson_ids)
                .execute()
            )

            progress_records = progress_response.data or []

            completed_lessons = sum(
                1 for record in progress_records
                if record.get("is_completed") is True
            )

            pending_lessons = sum(
                1 for record in progress_records
                if record.get("is_completed") is False
            )

        total_progress_records = (
            completed_lessons + pending_lessons
        )

        completion_rate = (
            round(
                (completed_lessons / total_progress_records) * 100,
                2
            )
            if total_progress_records else 0
        )

        return {
            "msg": "Analytics retrieved successfully",
            "data": {
                "total_courses": len(courses),
                "total_students": total_students,
                "total_lessons": total_lessons,
                "completed_lessons": completed_lessons,
                "pending_lessons": pending_lessons,
                "completion_rate": completion_rate
            }
        }

    except Exception as error:
        print("TRAINER ANALYTICS ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve trainer analytics."
        )
