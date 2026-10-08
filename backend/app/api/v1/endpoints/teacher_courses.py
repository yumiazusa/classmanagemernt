from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentTeacher, DBSession
from app.crud import crud_course
from app.schemas.course import ClassGroupPage, CourseRead

router = APIRouter(prefix="/teacher", tags=["teacher-courses"])


@router.get("/courses", response_model=list[CourseRead])
def get_teacher_courses(db: DBSession, teacher_user: CurrentTeacher) -> list[CourseRead]:
    return [CourseRead.model_validate(item) for item in crud_course.list_assigned_teacher_courses(db, teacher_id=teacher_user.id)]


def _require_teacher_course(db: DBSession, *, course_id: int, teacher_id: int) -> None:
    if not crud_course.teacher_has_course(db, course_id=course_id, teacher_id=teacher_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")


@router.get("/courses/{course_id}", response_model=CourseRead)
def get_teacher_course(course_id: int, db: DBSession, teacher_user: CurrentTeacher) -> CourseRead:
    _require_teacher_course(db, course_id=course_id, teacher_id=teacher_user.id)
    return CourseRead.model_validate(crud_course.get_course_read(db, course_id))


@router.get("/classes", response_model=ClassGroupPage)
def get_teacher_classes(
    db: DBSession,
    teacher_user: CurrentTeacher,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
) -> ClassGroupPage:
    _ = teacher_user
    crud_course.sync_class_members_from_user_class_names(db)
    return ClassGroupPage(**crud_course.list_classes(db, page=page, page_size=page_size, keyword=keyword))
