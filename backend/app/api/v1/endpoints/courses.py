from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentSubmissionUser, CurrentUser, DBSession
from app.crud import crud_course, crud_doc
from app.schemas.doc import CourseDocRead
from app.schemas.course import CourseModuleRead, CourseRead, CourseTaskRead, TaskSubmissionCreate, TaskSubmissionRead

router = APIRouter(tags=["courses"])


def _require_course_access(db: DBSession, course_id: int, current_user: CurrentUser) -> None:
    if not crud_course.can_access_course(db, course_id, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")


@router.get("/courses", response_model=list[CourseRead])
def list_courses(db: DBSession, current_user: CurrentUser) -> list[CourseRead]:
    return [CourseRead.model_validate(item) for item in crud_course.list_visible_courses(db, user=current_user)]


@router.get("/courses/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: DBSession, current_user: CurrentUser) -> CourseRead:
    _require_course_access(db, course_id, current_user)
    item = crud_course.get_course_read(db, course_id=course_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    return CourseRead.model_validate(item)


@router.get("/courses/{course_id}/docs", response_model=list[CourseDocRead])
def list_course_docs(course_id: int, db: DBSession, current_user: CurrentUser) -> list[CourseDocRead]:
    if not (current_user.role == "teacher" and crud_course.teacher_has_course(db, course_id=course_id, teacher_id=current_user.id)):
        _require_course_access(db, course_id, current_user)
    return [CourseDocRead.model_validate(doc) for doc in crud_doc.list_course_docs(db, course_id=course_id)]


@router.get("/courses/{course_id}/modules", response_model=list[CourseModuleRead])
def list_course_modules(course_id: int, db: DBSession, current_user: CurrentUser) -> list[CourseModuleRead]:
    _require_course_access(db, course_id, current_user)
    include_unpublished = current_user.role in {"teacher", "admin"}
    return [
        CourseModuleRead.model_validate(item)
        for item in crud_course.list_modules(db, course_id=course_id, include_unpublished=include_unpublished)
    ]


@router.get("/courses/{course_id}/tasks", response_model=list[CourseTaskRead])
def list_course_tasks(course_id: int, db: DBSession, current_user: CurrentUser) -> list[CourseTaskRead]:
    _require_course_access(db, course_id, current_user)
    include_unpublished = current_user.role in {"teacher", "admin"}
    return [
        CourseTaskRead.model_validate(item)
        for item in crud_course.list_tasks(
            db,
            course_id=course_id,
            user_id=current_user.id,
            include_unpublished=include_unpublished,
        )
    ]


@router.get("/tasks/{task_id}", response_model=CourseTaskRead)
def get_task(task_id: int, db: DBSession, current_user: CurrentUser) -> CourseTaskRead:
    from app.models.course import CourseTask
    task = db.get(CourseTask, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    _require_course_access(db, task.course_id, current_user)
    if current_user.role == "student" and not task.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    item = crud_course.get_task_read(db, task_id=task_id, user_id=current_user.id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    return CourseTaskRead.model_validate(item)


@router.post("/tasks/{task_id}/submissions", response_model=TaskSubmissionRead, status_code=status.HTTP_201_CREATED)
def submit_task(
    task_id: int,
    payload: TaskSubmissionCreate,
    db: DBSession,
    current_user: CurrentSubmissionUser,
) -> TaskSubmissionRead:
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="管理员账号不支持提交任务")
    get_task(task_id, db, current_user)
    created = crud_course.create_submission(db, task_id=task_id, user_id=current_user.id, payload=payload.model_dump())
    return TaskSubmissionRead.model_validate(created)
