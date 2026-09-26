from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.models.course import ClassGroup, ClassMember, Course, CourseClass, CourseTask, TaskSubmission
from app.models.user import User


def _latest_user_submissions_subquery(*, user_id: int):
    latest_version_subquery = (
        select(TaskSubmission.task_id.label("task_id"), func.max(TaskSubmission.version).label("latest_version"))
        .where(TaskSubmission.user_id == user_id)
        .group_by(TaskSubmission.task_id)
        .subquery()
    )
    return (
        select(
            TaskSubmission.id.label("submission_id"),
            TaskSubmission.task_id.label("task_id"),
            TaskSubmission.status.label("latest_status"),
            TaskSubmission.review_status.label("review_status"),
            TaskSubmission.updated_at.label("latest_updated_at"),
        )
        .join(
            latest_version_subquery,
            (TaskSubmission.task_id == latest_version_subquery.c.task_id)
            & (TaskSubmission.version == latest_version_subquery.c.latest_version),
        )
        .where(TaskSubmission.user_id == user_id)
        .subquery()
    )


def _visible_course_ids_for_user(db: Session, user: User) -> list[int]:
    statement = (
        select(Course.id)
        .select_from(Course)
        .outerjoin(CourseClass, CourseClass.course_id == Course.id)
        .outerjoin(ClassGroup, ClassGroup.id == CourseClass.class_group_id)
        .outerjoin(ClassMember, ClassMember.class_group_id == ClassGroup.id)
        .where(
            Course.is_active.is_(True),
            Course.status == "published",
            or_(ClassMember.user_id == user.id, ClassGroup.name == (user.class_name or "")),
        )
        .distinct()
    )
    return [int(item) for item in db.execute(statement).scalars().all()]


def get_dashboard_payload(db: Session, *, user_id: int) -> dict | None:
    user = db.get(User, user_id)
    if not user:
        return None

    course_ids = _visible_course_ids_for_user(db, user)
    visible_tasks_subquery = (
        select(
            CourseTask.id.label("task_id"),
            CourseTask.course_id.label("course_id"),
            CourseTask.title.label("title"),
            CourseTask.task_type.label("task_type"),
            Course.title.label("course_title"),
        )
        .join(Course, Course.id == CourseTask.course_id)
        .where(CourseTask.course_id.in_(course_ids) if course_ids else False, CourseTask.is_published.is_(True))
        .subquery()
    )
    latest_user_subquery = _latest_user_submissions_subquery(user_id=user_id)

    summary_statement = (
        select(
            func.count(visible_tasks_subquery.c.task_id).label("total_tasks"),
            func.sum(case((latest_user_subquery.c.latest_status == "submitted", 1), else_=0)).label("submitted_count"),
            func.sum(case((latest_user_subquery.c.review_status.in_(["reviewed", "passed"]), 1), else_=0)).label("reviewed_count"),
            func.sum(case((latest_user_subquery.c.review_status == "returned", 1), else_=0)).label("returned_count"),
            func.sum(case((latest_user_subquery.c.review_status == "pending", 1), else_=0)).label("pending_count"),
            func.sum(case((latest_user_subquery.c.submission_id.is_(None), 1), else_=0)).label("not_started_count"),
        )
        .select_from(visible_tasks_subquery)
        .outerjoin(latest_user_subquery, latest_user_subquery.c.task_id == visible_tasks_subquery.c.task_id)
    )
    summary_row = db.execute(summary_statement).one()

    recent_statement = (
        select(
            visible_tasks_subquery.c.task_id,
            visible_tasks_subquery.c.course_id,
            visible_tasks_subquery.c.title,
            visible_tasks_subquery.c.course_title,
            visible_tasks_subquery.c.task_type,
            latest_user_subquery.c.latest_status,
            latest_user_subquery.c.review_status,
            latest_user_subquery.c.latest_updated_at,
        )
        .select_from(latest_user_subquery)
        .join(visible_tasks_subquery, visible_tasks_subquery.c.task_id == latest_user_subquery.c.task_id)
        .order_by(latest_user_subquery.c.latest_updated_at.desc(), latest_user_subquery.c.task_id.asc())
        .limit(5)
    )
    recent_rows = db.execute(recent_statement).all()

    return {
        "profile": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "student_no": user.student_no,
            "class_name": user.class_name,
            "role": user.role,
        },
        "summary": {
            "total_courses": len(course_ids),
            "total_tasks": int(summary_row.total_tasks or 0),
            "submitted_count": int(summary_row.submitted_count or 0),
            "reviewed_count": int(summary_row.reviewed_count or 0),
            "returned_count": int(summary_row.returned_count or 0),
            "pending_count": int(summary_row.pending_count or 0),
            "not_started_count": int(summary_row.not_started_count or 0),
        },
        "recent_items": [
            {
                "task_id": row.task_id,
                "course_id": row.course_id,
                "title": row.title,
                "course_title": row.course_title,
                "task_type": row.task_type,
                "latest_status": row.latest_status,
                "review_status": row.review_status or "pending",
                "latest_updated_at": row.latest_updated_at,
            }
            for row in recent_rows
        ],
    }
