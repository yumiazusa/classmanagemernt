from datetime import datetime, timezone
from math import ceil

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.models.course import (
    ClassGroup,
    ClassMember,
    Course,
    CourseClass,
    CourseModule,
    CourseTask,
    CourseTeacher,
    TaskSubmission,
)
from app.models.user import User


def _clean_text(value):
    if isinstance(value, str):
        return value.strip() or None
    return value


def _page(statement, db: Session, page: int, page_size: int) -> dict:
    total = int(db.execute(select(func.count()).select_from(statement.subquery())).scalar_one() or 0)
    total_pages = ceil(total / page_size) if total > 0 else 0
    rows = list(db.execute(statement.offset((page - 1) * page_size).limit(page_size)).all())
    return {"rows": rows, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


def _course_counts_subqueries():
    teachers = select(CourseTeacher.course_id, func.count(CourseTeacher.id).label("teacher_count")).group_by(CourseTeacher.course_id).subquery()
    classes = select(CourseClass.course_id, func.count(CourseClass.id).label("class_count")).group_by(CourseClass.course_id).subquery()
    modules = select(CourseModule.course_id, func.count(CourseModule.id).label("module_count")).group_by(CourseModule.course_id).subquery()
    tasks = select(CourseTask.course_id, func.count(CourseTask.id).label("task_count")).group_by(CourseTask.course_id).subquery()
    return teachers, classes, modules, tasks


def _course_select():
    teachers, classes, modules, tasks = _course_counts_subqueries()
    return (
        select(
            Course,
            func.coalesce(teachers.c.teacher_count, 0).label("teacher_count"),
            func.coalesce(classes.c.class_count, 0).label("class_count"),
            func.coalesce(modules.c.module_count, 0).label("module_count"),
            func.coalesce(tasks.c.task_count, 0).label("task_count"),
        )
        .outerjoin(teachers, teachers.c.course_id == Course.id)
        .outerjoin(classes, classes.c.course_id == Course.id)
        .outerjoin(modules, modules.c.course_id == Course.id)
        .outerjoin(tasks, tasks.c.course_id == Course.id)
    )


def _map_course_row(row) -> dict:
    course = row.Course if hasattr(row, "Course") else row[0]
    return {
        "id": course.id,
        "title": course.title,
        "slug": course.slug,
        "summary": course.summary,
        "description": course.description,
        "status": course.status,
        "cover_color": course.cover_color,
        "sort_order": course.sort_order or 0,
        "is_active": bool(course.is_active),
        "teacher_count": int(row.teacher_count or 0),
        "class_count": int(row.class_count or 0),
        "module_count": int(row.module_count or 0),
        "task_count": int(row.task_count or 0),
        "created_at": course.created_at,
        "updated_at": course.updated_at,
    }


def get_course(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)


def get_course_by_slug(db: Session, slug: str) -> Course | None:
    return db.execute(select(Course).where(Course.slug == slug)).scalar_one_or_none()


def get_course_read(db: Session, course_id: int) -> dict | None:
    statement = _course_select().where(Course.id == course_id)
    row = db.execute(statement).first()
    return _map_course_row(row) if row else None


def list_visible_courses(db: Session, *, user: User) -> list[dict]:
    statement = _course_select().where(Course.is_active.is_(True), Course.status == "published")
    if user.role == "teacher":
        statement = statement.join(CourseTeacher, CourseTeacher.course_id == Course.id).where(CourseTeacher.teacher_id == user.id)
    elif user.role == "student":
        statement = (
            statement.outerjoin(CourseClass, CourseClass.course_id == Course.id)
            .outerjoin(ClassGroup, ClassGroup.id == CourseClass.class_group_id)
            .outerjoin(ClassMember, ClassMember.class_group_id == ClassGroup.id)
            .where(
                or_(
                    ClassMember.user_id == user.id,
                    ClassGroup.name == (user.class_name or ""),
                )
            )
        )
    statement = statement.order_by(Course.sort_order.asc(), Course.id.asc()).distinct()
    return [_map_course_row(row) for row in db.execute(statement).all()]


def list_admin_courses(db: Session, *, page: int, page_size: int, keyword: str = "", status: str = "all") -> dict:
    statement = _course_select()
    clean_keyword = keyword.strip()
    if clean_keyword:
        statement = statement.where(or_(Course.title.ilike(f"%{clean_keyword}%"), Course.slug.ilike(f"%{clean_keyword}%")))
    if status in {"draft", "published", "archived"}:
        statement = statement.where(Course.status == status)
    statement = statement.order_by(Course.sort_order.asc(), Course.id.desc())
    data = _page(statement, db, page, page_size)
    data["items"] = [_map_course_row(row) for row in data.pop("rows")]
    return data


def _sync_course_links(db: Session, course: Course, *, teacher_ids: list[int] | None, class_group_ids: list[int] | None) -> None:
    if teacher_ids is not None:
        db.query(CourseTeacher).filter(CourseTeacher.course_id == course.id).delete()
        for teacher_id in dict.fromkeys(teacher_ids):
            teacher = db.get(User, teacher_id)
            if teacher and teacher.role == "teacher":
                db.add(CourseTeacher(course_id=course.id, teacher_id=teacher_id))
    if class_group_ids is not None:
        db.query(CourseClass).filter(CourseClass.course_id == course.id).delete()
        for class_group_id in dict.fromkeys(class_group_ids):
            if db.get(ClassGroup, class_group_id):
                db.add(CourseClass(course_id=course.id, class_group_id=class_group_id))


def create_course(db: Session, payload: dict) -> Course:
    teacher_ids = payload.pop("teacher_ids", [])
    class_group_ids = payload.pop("class_group_ids", [])
    for key in {"title", "slug", "summary", "description", "cover_color"}:
        payload[key] = _clean_text(payload.get(key))
    course = Course(**payload)
    db.add(course)
    db.flush()
    _sync_course_links(db, course, teacher_ids=teacher_ids, class_group_ids=class_group_ids)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course: Course, payload: dict) -> Course:
    teacher_ids = payload.pop("teacher_ids", None)
    class_group_ids = payload.pop("class_group_ids", None)
    for key, value in payload.items():
        setattr(course, key, _clean_text(value) if key in {"title", "slug", "summary", "description", "cover_color"} else value)
    db.add(course)
    _sync_course_links(db, course, teacher_ids=teacher_ids, class_group_ids=class_group_ids)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course: Course) -> None:
    db.delete(course)
    db.commit()


def list_modules(db: Session, course_id: int, *, include_unpublished: bool = False) -> list[dict]:
    task_counts = select(CourseTask.module_id, func.count(CourseTask.id).label("task_count")).group_by(CourseTask.module_id).subquery()
    statement = (
        select(CourseModule, func.coalesce(task_counts.c.task_count, 0).label("task_count"))
        .outerjoin(task_counts, task_counts.c.module_id == CourseModule.id)
        .where(CourseModule.course_id == course_id)
        .order_by(CourseModule.sort_order.asc(), CourseModule.id.asc())
    )
    if not include_unpublished:
        statement = statement.where(CourseModule.is_published.is_(True))
    rows = db.execute(statement).all()
    return [
        {
            "id": row.CourseModule.id,
            "course_id": row.CourseModule.course_id,
            "title": row.CourseModule.title,
            "summary": row.CourseModule.summary,
            "sort_order": row.CourseModule.sort_order or 0,
            "is_published": bool(row.CourseModule.is_published),
            "task_count": int(row.task_count or 0),
            "created_at": row.CourseModule.created_at,
            "updated_at": row.CourseModule.updated_at,
        }
        for row in rows
    ]


def create_module(db: Session, payload: dict) -> CourseModule:
    module = CourseModule(**payload)
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


def list_tasks(db: Session, course_id: int, *, user_id: int | None = None, include_unpublished: bool = False) -> list[dict]:
    latest_version = (
        select(TaskSubmission.task_id, func.max(TaskSubmission.version).label("latest_version"))
        .where(TaskSubmission.user_id == user_id if user_id else True)
        .group_by(TaskSubmission.task_id)
        .subquery()
    )
    latest_submission = (
        select(TaskSubmission)
        .join(latest_version, (TaskSubmission.task_id == latest_version.c.task_id) & (TaskSubmission.version == latest_version.c.latest_version))
        .subquery()
    )
    statement = (
        select(CourseTask, latest_submission.c.id.label("latest_submission_id"), latest_submission.c.status, latest_submission.c.review_status)
        .outerjoin(latest_submission, latest_submission.c.task_id == CourseTask.id)
        .where(CourseTask.course_id == course_id)
        .order_by(CourseTask.sort_order.asc(), CourseTask.id.asc())
    )
    if not include_unpublished:
        statement = statement.where(CourseTask.is_published.is_(True))
    rows = db.execute(statement).all()
    return [_map_task_row(row) for row in rows]


def _map_task_row(row) -> dict:
    task = row.CourseTask if hasattr(row, "CourseTask") else row[0]
    return {
        "id": task.id,
        "course_id": task.course_id,
        "module_id": task.module_id,
        "title": task.title,
        "task_type": task.task_type,
        "summary": task.summary,
        "instruction_content": task.instruction_content,
        "external_url": task.external_url,
        "config": task.config,
        "sort_order": task.sort_order or 0,
        "max_score": task.max_score,
        "is_required": bool(task.is_required),
        "is_published": bool(task.is_published),
        "open_at": task.open_at,
        "due_at": task.due_at,
        "latest_submission_id": getattr(row, "latest_submission_id", None),
        "latest_submission_status": getattr(row, "status", None),
        "review_status": getattr(row, "review_status", None),
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


def get_task_read(db: Session, task_id: int, *, user_id: int | None = None) -> dict | None:
    task = db.get(CourseTask, task_id)
    if not task:
        return None
    row = type("TaskRow", (), {})()
    row.CourseTask = task
    latest = get_latest_submission(db, task_id=task_id, user_id=user_id) if user_id else None
    row.latest_submission_id = latest.id if latest else None
    row.status = latest.status if latest else None
    row.review_status = latest.review_status if latest else None
    return _map_task_row(row)


def create_task(db: Session, payload: dict) -> CourseTask:
    task = CourseTask(**payload)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: CourseTask, payload: dict) -> CourseTask:
    for key, value in payload.items():
        setattr(task, key, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_latest_submission(db: Session, *, task_id: int, user_id: int) -> TaskSubmission | None:
    statement = (
        select(TaskSubmission)
        .where(TaskSubmission.task_id == task_id, TaskSubmission.user_id == user_id)
        .order_by(TaskSubmission.version.desc())
        .limit(1)
    )
    return db.execute(statement).scalar_one_or_none()


def create_submission(db: Session, *, task_id: int, user_id: int, payload: dict) -> TaskSubmission:
    latest = get_latest_submission(db, task_id=task_id, user_id=user_id)
    submission = TaskSubmission(task_id=task_id, user_id=user_id, version=(latest.version + 1 if latest else 1), **payload)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def list_task_submissions(db: Session, *, task_id: int) -> list[dict]:
    statement = (
        select(TaskSubmission, User.username, User.full_name, User.student_no, User.class_name, CourseTask.title.label("task_title"), Course.title.label("course_title"))
        .join(User, User.id == TaskSubmission.user_id)
        .join(CourseTask, CourseTask.id == TaskSubmission.task_id)
        .join(Course, Course.id == CourseTask.course_id)
        .where(TaskSubmission.task_id == task_id)
        .order_by(TaskSubmission.updated_at.desc(), TaskSubmission.id.desc())
    )
    return [_map_submission_row(row) for row in db.execute(statement).all()]


def _map_submission_row(row) -> dict:
    submission = row.TaskSubmission
    return {
        "id": submission.id,
        "task_id": submission.task_id,
        "user_id": submission.user_id,
        "content": submission.content,
        "attachment_url": submission.attachment_url,
        "status": submission.status,
        "score": submission.score,
        "review_status": submission.review_status,
        "review_comment": submission.review_comment,
        "reviewed_by": submission.reviewed_by,
        "reviewed_at": submission.reviewed_at,
        "version": submission.version,
        "created_at": submission.created_at,
        "updated_at": submission.updated_at,
        "username": row.username,
        "full_name": row.full_name,
        "student_no": row.student_no,
        "class_name": row.class_name,
        "task_title": row.task_title,
        "course_title": row.course_title,
    }


def review_submission(db: Session, *, submission_id: int, reviewer_id: int, payload: dict) -> TaskSubmission | None:
    submission = db.get(TaskSubmission, submission_id)
    if not submission:
        return None
    submission.review_status = payload["review_status"]
    submission.score = payload.get("score")
    submission.review_comment = _clean_text(payload.get("review_comment"))
    submission.reviewed_by = reviewer_id
    submission.reviewed_at = datetime.now(timezone.utc)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def list_classes(db: Session, *, page: int, page_size: int, keyword: str = "") -> dict:
    member_counts = select(ClassMember.class_group_id, func.count(ClassMember.id).label("member_count")).group_by(ClassMember.class_group_id).subquery()
    course_counts = select(CourseClass.class_group_id, func.count(CourseClass.id).label("course_count")).group_by(CourseClass.class_group_id).subquery()
    statement = (
        select(ClassGroup, func.coalesce(member_counts.c.member_count, 0).label("member_count"), func.coalesce(course_counts.c.course_count, 0).label("course_count"))
        .outerjoin(member_counts, member_counts.c.class_group_id == ClassGroup.id)
        .outerjoin(course_counts, course_counts.c.class_group_id == ClassGroup.id)
    )
    clean_keyword = keyword.strip()
    if clean_keyword:
        statement = statement.where(ClassGroup.name.ilike(f"%{clean_keyword}%"))
    statement = statement.order_by(ClassGroup.created_at.desc(), ClassGroup.id.desc())
    data = _page(statement, db, page, page_size)
    data["items"] = [
        {
            "id": row.ClassGroup.id,
            "name": row.ClassGroup.name,
            "grade": row.ClassGroup.grade,
            "description": row.ClassGroup.description,
            "is_active": bool(row.ClassGroup.is_active),
            "member_count": int(row.member_count or 0),
            "course_count": int(row.course_count or 0),
            "created_at": row.ClassGroup.created_at,
            "updated_at": row.ClassGroup.updated_at,
        }
        for row in data.pop("rows")
    ]
    return data


def create_class(db: Session, payload: dict) -> ClassGroup:
    class_group = ClassGroup(**payload)
    db.add(class_group)
    db.commit()
    db.refresh(class_group)
    return class_group


def sync_class_members_from_user_class_names(db: Session) -> None:
    groups = {group.name: group for group in db.execute(select(ClassGroup)).scalars().all()}
    students = db.execute(select(User).where(User.role == "student", User.class_name.is_not(None), User.class_name != "")).scalars().all()
    for student in students:
        group = groups.get(student.class_name)
        if not group:
            group = ClassGroup(name=student.class_name, is_active=True)
            db.add(group)
            db.flush()
            groups[group.name] = group
        exists = db.execute(
            select(ClassMember.id).where(ClassMember.class_group_id == group.id, ClassMember.user_id == student.id)
        ).scalar_one_or_none()
        if not exists:
            db.add(ClassMember(class_group_id=group.id, user_id=student.id))
    db.commit()
