from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentSubmissionUser, CurrentUser, DBSession
from app.crud import crud_course
from app.schemas.course import CourseModuleRead, CourseRead, CourseTaskRead, TaskSubmissionCreate, TaskSubmissionRead

router = APIRouter(tags=["courses"])


@router.get("/courses", response_model=list[CourseRead])
def list_courses(db: DBSession, current_user: CurrentUser) -> list[CourseRead]:
    return [CourseRead.model_validate(item) for item in crud_course.list_visible_courses(db, user=current_user)]


@router.get("/courses/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: DBSession, current_user: CurrentUser) -> CourseRead:
    _ = current_user
    item = crud_course.get_course_read(db, course_id=course_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    return CourseRead.model_validate(item)


@router.get("/courses/{course_id}/modules", response_model=list[CourseModuleRead])
def list_course_modules(course_id: int, db: DBSession, current_user: CurrentUser) -> list[CourseModuleRead]:
    include_unpublished = current_user.role in {"teacher", "admin"}
    return [
        CourseModuleRead.model_validate(item)
        for item in crud_course.list_modules(db, course_id=course_id, include_unpublished=include_unpublished)
    ]


@router.get("/courses/{course_id}/tasks", response_model=list[CourseTaskRead])
def list_course_tasks(course_id: int, db: DBSession, current_user: CurrentUser) -> list[CourseTaskRead]:
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
    if not crud_course.get_task_read(db, task_id=task_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    created = crud_course.create_submission(db, task_id=task_id, user_id=current_user.id, payload=payload.model_dump())
    return TaskSubmissionRead.model_validate(created)
