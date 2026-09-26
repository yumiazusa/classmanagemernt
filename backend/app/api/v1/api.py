from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.admin_courses import router as admin_courses_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.courses import router as courses_router
from app.api.v1.endpoints.docs import router as docs_router
from app.api.v1.endpoints.student import router as student_router
from app.api.v1.endpoints.teacher import router as teacher_router
from app.api.v1.endpoints.teacher_courses import router as teacher_courses_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(docs_router)
api_v1_router.include_router(courses_router)
api_v1_router.include_router(teacher_router)
api_v1_router.include_router(teacher_courses_router)
api_v1_router.include_router(student_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(admin_courses_router)
