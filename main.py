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
            detail="Unable to retrieve enrolled courses"
        )


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
        # Verify that the course exists and is published
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

        # Check whether the student is already enrolled
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

        # Create the enrollment
        result = (
            supabase_obj.table("enrollments")
            .insert({
                "student_id": student_id,
                "course_id": course_id,
                "status": "active"
            })
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Enrollment was not saved."
            )

        return {
            "msg": "Course enrollment successful.",
            "data": result.data[0]
        }

    except HTTPException:
        raise

    except Exception as error:

        print("\n========== ENROLLMENT ERROR ==========")
        traceback.print_exc()
        print("======================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )



@fastapi_obj.get("/get_published_courses")
def get_published_courses():
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

@fastapi_obj.delete("/deleteCourse/{c_id}")
def courseDelete(c_id:str):
    res_from_supabase_after_c_delete=supabase_obj.table("courses").delete().eq("id",c_id).execute()
    print(res_from_supabase_after_c_delete.data[0])
    return {
        "msg":f"{res_from_supabase_after_c_delete.data[0]["course_name"]} course deleted successfully"
    }


@fastapi_obj.get("/get_my_courses")
def get_my_courses_fun(t_id:str):
    res=supabase_obj.table("courses").select("*").eq("trainer_id",t_id).execute()
    return {

"msg":"got yr courses records",
"data":res.data
    }
    # select *
# from courses 
# where trainer_id = "a53738a9-3e62-4e8d-bcd4-911415f8530d"


@fastapi_obj.post("/add_course")
def add_course_fun(new_course:dict):
    res_from_sup=supabase_obj.table("courses").insert(new_course).execute()
    print(res_from_sup)
    return {
        "msg":"successfully added a new course"
    }


@fastapi_obj.post("/login")
def login_validation(login_cred_details:dict):
    print(login_cred_details)

    incoming_login_email=login_cred_details["email"]
    incoming_login_password=login_cred_details["password"]
    incoming_login_role=login_cred_details["role"]

    response = supabase_obj.table("users") \
    .select("id,name,email,role") \
    .eq("email", incoming_login_email) \
    .eq("password", incoming_login_password) \
    .eq("role", incoming_login_role) \
    .execute()

    print(response.data,"res from supabase after login")

    if len(response.data) == 0:
        return {
            "msg":"invalid credentials"
        }

    return {
        "msg":"login successful",
        "status":True,
        "loggedIn_user":response.data[0]
    }

@fastapi_obj.post("/register")
def user_registration(new_user:dict): # type annotation
    print("reg function")
    print(new_user)
    res=supabase_obj.table("users").insert(new_user).execute()

    return{
        "msg":"reg done successfully",
        "data":res.data
    }

# how to start be server ?

# uvicorn main:fastapi_obj --reload


# select *
# from users
# where email ="" and password="" and role=""