from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentTeacher, DBSession
from app.crud import crud_course
from app.schemas.course import ClassGroupPage, CourseRead, TaskSubmissionReviewUpdate, TeacherSubmissionItem

router = APIRouter(prefix="/teacher", tags=["teacher-courses"])


@router.get("/courses", response_model=list[CourseRead])
def get_teacher_courses(db: DBSession, teacher_user: CurrentTeacher) -> list[CourseRead]:
    return [CourseRead.model_validate(item) for item in crud_course.list_visible_courses(db, user=teacher_user)]


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


@router.get("/tasks/{task_id}/submissions", response_model=list[TeacherSubmissionItem])
def get_teacher_task_submissions(task_id: int, db: DBSession, teacher_user: CurrentTeacher) -> list[TeacherSubmissionItem]:
    _ = teacher_user
    if not crud_course.get_task_read(db, task_id=task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    return [TeacherSubmissionItem.model_validate(item) for item in crud_course.list_task_submissions(db, task_id=task_id)]


@router.post("/submissions/{submission_id}/review", response_model=TeacherSubmissionItem)
def review_teacher_submission(
    submission_id: int,
    payload: TaskSubmissionReviewUpdate,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherSubmissionItem:
    reviewed = crud_course.review_submission(
        db,
        submission_id=submission_id,
        reviewer_id=teacher_user.id,
        payload=payload.model_dump(),
    )
    if not reviewed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提交不存在")
    rows = crud_course.list_task_submissions(db, task_id=reviewed.task_id)
    item = next((row for row in rows if row["id"] == reviewed.id), None)
    return TeacherSubmissionItem.model_validate(item)
