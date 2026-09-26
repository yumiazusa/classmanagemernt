from datetime import datetime, timedelta
from math import ceil

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.course import Course, TaskSubmission
from app.models.user import User

VALID_ROLE_FILTERS = {"student", "teacher", "admin"}


def get_overview_stats(db: Session) -> dict:
    since = datetime.utcnow() - timedelta(days=7)

    total_users = db.execute(select(func.count(User.id))).scalar_one() or 0
    student_count = db.execute(select(func.count(User.id)).where(User.role == "student")).scalar_one() or 0
    teacher_count = db.execute(select(func.count(User.id)).where(User.role == "teacher")).scalar_one() or 0
    admin_count = db.execute(select(func.count(User.id)).where(User.role == "admin")).scalar_one() or 0

    course_count = db.execute(select(func.count(Course.id))).scalar_one() or 0

    enabled_user_count = db.execute(select(func.count(User.id)).where(User.is_enabled.is_(True))).scalar_one() or 0
    disabled_user_count = db.execute(select(func.count(User.id)).where(User.is_enabled.is_(False))).scalar_one() or 0

    recent_created_users_count = (
        db.execute(select(func.count(User.id)).where(User.created_at >= since)).scalar_one() or 0
    )
    recent_submission_count = (
        db.execute(select(func.count(TaskSubmission.id)).where(TaskSubmission.created_at >= since)).scalar_one() or 0
    )

    return {
        "total_users": int(total_users),
        "student_count": int(student_count),
        "teacher_count": int(teacher_count),
        "admin_count": int(admin_count),
        "course_count": int(course_count),
        "experiment_count": int(course_count),
        "enabled_user_count": int(enabled_user_count),
        "disabled_user_count": int(disabled_user_count),
        "recent_created_users_count": int(recent_created_users_count),
        "recent_submission_count": int(recent_submission_count),
    }


def _build_users_statement(
    *,
    keyword: str = "",
    role_filter: str = "all",
    class_name: str = "",
    is_enabled: bool | None = None,
):
    statement = select(
        User.id.label("user_id"),
        User.username.label("username"),
        User.full_name.label("full_name"),
        User.role.label("role"),
        User.student_no.label("student_no"),
        User.class_name.label("class_name"),
        User.is_enabled.label("is_enabled"),
        User.created_at.label("created_at"),
    )

    clean_keyword = keyword.strip()
    if clean_keyword:
        statement = statement.where(
            or_(
                User.username.ilike(f"%{clean_keyword}%"),
                User.full_name.ilike(f"%{clean_keyword}%"),
                User.student_no.ilike(f"%{clean_keyword}%"),
            )
        )

    if role_filter in VALID_ROLE_FILTERS:
        statement = statement.where(User.role == role_filter)

    clean_class_name = class_name.strip()
    if clean_class_name:
        statement = statement.where(User.class_name.ilike(f"%{clean_class_name}%"))

    if is_enabled is not None:
        statement = statement.where(User.is_enabled == is_enabled)

    return statement.order_by(User.created_at.desc(), User.id.asc())


def _map_user_row(row) -> dict:
    return {
        "user_id": row.user_id,
        "username": row.username,
        "full_name": row.full_name,
        "role": row.role,
        "student_no": row.student_no,
        "class_name": row.class_name,
        "is_enabled": bool(row.is_enabled),
        "created_at": row.created_at,
    }


def list_users(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    role_filter: str = "all",
    class_name: str = "",
    is_enabled: bool | None = None,
) -> dict:
    statement = _build_users_statement(
        keyword=keyword,
        role_filter=role_filter,
        class_name=class_name,
        is_enabled=is_enabled,
    )
    total_statement = select(func.count()).select_from(statement.subquery())
    total = db.execute(total_statement).scalar_one() or 0
    total_pages = ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size
    rows = db.execute(statement.offset(offset).limit(page_size)).all()

    return {
        "items": [_map_user_row(row) for row in rows],
        "total": int(total),
        "page": int(page),
        "page_size": int(page_size),
        "total_pages": int(total_pages),
    }


def create_teacher(
    db: Session,
    *,
    username: str,
    full_name: str | None,
    password: str,
) -> User:
    teacher = User(
        username=username.strip(),
        password_hash=get_password_hash(password),
        role="teacher",
        full_name=(full_name.strip() if isinstance(full_name, str) and full_name.strip() else None),
        must_change_password=True,
        is_enabled=True,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


def create_admin_account(
    db: Session,
    *,
    username: str,
    full_name: str | None,
    password: str,
) -> User:
    admin_user = User(
        username=username.strip(),
        password_hash=get_password_hash(password),
        role="admin",
        full_name=(full_name.strip() if isinstance(full_name, str) and full_name.strip() else None),
        must_change_password=True,
        is_enabled=True,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user


def list_admin_accounts(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    is_enabled: bool | None = None,
) -> dict:
    statement = select(
        User.id.label("user_id"),
        User.username.label("username"),
        User.full_name.label("full_name"),
        User.role.label("role"),
        User.is_enabled.label("is_enabled"),
        User.must_change_password.label("must_change_password"),
        User.created_at.label("created_at"),
    ).where(User.role == "admin")

    clean_keyword = keyword.strip()
    if clean_keyword:
        statement = statement.where(
            or_(
                User.username.ilike(f"%{clean_keyword}%"),
                User.full_name.ilike(f"%{clean_keyword}%"),
            )
        )

    if is_enabled is not None:
        statement = statement.where(User.is_enabled == is_enabled)

    statement = statement.order_by(User.created_at.desc(), User.id.asc())
    total_statement = select(func.count()).select_from(statement.subquery())
    total = db.execute(total_statement).scalar_one() or 0
    total_pages = ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size
    rows = db.execute(statement.offset(offset).limit(page_size)).all()
    items = [
        {
            "user_id": row.user_id,
            "username": row.username,
            "full_name": row.full_name,
            "role": row.role,
            "is_enabled": bool(row.is_enabled),
            "must_change_password": bool(row.must_change_password),
            "created_at": row.created_at,
        }
        for row in rows
    ]
    return {
        "items": items,
        "total": int(total),
        "page": int(page),
        "page_size": int(page_size),
        "total_pages": int(total_pages),
    }


def count_enabled_admin_accounts(db: Session) -> int:
    return int(db.execute(select(func.count(User.id)).where(User.role == "admin", User.is_enabled.is_(True))).scalar_one() or 0)


def count_admin_accounts(db: Session) -> int:
    return int(db.execute(select(func.count(User.id)).where(User.role == "admin")).scalar_one() or 0)


def set_admin_account_enabled(
    db: Session,
    *,
    target_user_id: int,
    is_enabled: bool,
    acting_admin_id: int,
) -> tuple[User | None, str | None]:
    user = db.get(User, target_user_id)
    if not user:
        return None, "用户不存在"
    if user.role != "admin":
        return None, "仅可操作管理员账号"
    if not is_enabled and user.id == acting_admin_id:
        return None, "不能停用当前登录的管理员账号"
    if not is_enabled and bool(user.is_enabled):
        enabled_count = count_enabled_admin_accounts(db)
        if enabled_count <= 1:
            return None, "系统必须至少保留一个启用中的管理员账号"

    user.is_enabled = is_enabled
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def reset_admin_account_password(
    db: Session,
    *,
    target_user_id: int,
    new_password: str,
) -> tuple[User | None, str | None]:
    user = db.get(User, target_user_id)
    if not user:
        return None, "用户不存在"
    if user.role != "admin":
        return None, "仅可操作管理员账号"
    user.password_hash = get_password_hash(new_password)
    user.must_change_password = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def set_user_role(
    db: Session,
    *,
    target_user_id: int,
    target_role: str,
    acting_admin_id: int,
) -> tuple[User | None, str | None]:
    user = db.get(User, target_user_id)
    if not user:
        return None, "用户不存在"
    if target_role not in VALID_ROLE_FILTERS:
        return None, "角色仅支持 student/teacher/admin"
    if user.id == acting_admin_id and target_role != "admin":
        return None, "不能修改当前登录管理员为非管理员角色"

    current_role = user.role
    if current_role == target_role:
        return user, None

    if current_role == "admin" and target_role != "admin":
        admin_count = count_admin_accounts(db)
        if admin_count <= 1:
            return None, "系统至少保留一个管理员账号"
        if bool(user.is_enabled):
            enabled_admin_count = count_enabled_admin_accounts(db)
            if enabled_admin_count <= 1:
                return None, "系统必须至少保留一个启用中的管理员账号"

    user.role = target_role
    if target_role in {"teacher", "admin"}:
        user.student_no = None
        user.class_name = None
    user.must_change_password = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def update_user_basic_info(
    db: Session,
    *,
    target_user_id: int,
    username: str,
    full_name: str | None,
) -> tuple[User | None, str | None]:
    user = db.get(User, target_user_id)
    if not user:
        return None, "用户不存在"

    cleaned_username = username.strip()
    if len(cleaned_username) < 3:
        return None, "用户名长度不能少于 3 位"

    existed = db.execute(select(User.id).where(User.username == cleaned_username, User.id != target_user_id)).scalar_one_or_none()
    if existed:
        return None, "用户名已存在"

    cleaned_full_name = full_name.strip() if isinstance(full_name, str) else ""
    user.username = cleaned_username
    user.full_name = cleaned_full_name or None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def set_user_enabled(
    db: Session,
    *,
    target_user_id: int,
    is_enabled: bool,
    acting_admin_id: int,
) -> tuple[User | None, str | None]:
    user = db.get(User, target_user_id)
    if not user:
        return None, "用户不存在"
    if user.role == "admin":
        return None, "管理员账号请在管理员管理页操作"
    if not is_enabled and user.id == acting_admin_id:
        return None, "不能停用当前登录管理员账号"

    user.is_enabled = is_enabled
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def reset_user_password(
    db: Session,
    *,
    target_user_id: int,
    new_password: str,
) -> tuple[User | None, str | None]:
    user = db.get(User, target_user_id)
    if not user:
        return None, "用户不存在"
    if user.role == "admin":
        return None, "管理员账号请在管理员管理页操作"

    user.password_hash = get_password_hash(new_password)
    user.must_change_password = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def list_user_class_options(db: Session) -> list[str]:
    statement = (
        select(User.class_name)
        .where(
            User.class_name.is_not(None),
            User.class_name != "",
        )
        .group_by(User.class_name)
        .order_by(User.class_name.asc())
    )
    rows = db.execute(statement).scalars().all()
    return [item for item in rows if isinstance(item, str) and item.strip()]


def delete_user(
    db: Session,
    *,
    target_user_id: int,
    acting_admin_id: int,
) -> tuple[bool, str | None]:
    user = db.get(User, target_user_id)
    if not user:
        return False, "用户不存在"
    if user.id == acting_admin_id:
        return False, "不能删除当前登录管理员账号"
    if user.role == "admin":
        admin_count = count_admin_accounts(db)
        if admin_count <= 1:
            return False, "系统至少保留一个管理员账号"
        if bool(user.is_enabled):
            enabled_admin_count = count_enabled_admin_accounts(db)
            if enabled_admin_count <= 1:
                return False, "系统必须至少保留一个启用中的管理员账号"

    db.delete(user)
    db.commit()
    return True, None


def batch_delete_users(
    db: Session,
    *,
    user_ids: list[int],
    acting_admin_id: int,
) -> tuple[list[int], list[dict]]:
    success_user_ids: list[int] = []
    failed_items: list[dict] = []
    seen_user_ids: set[int] = set()
    admin_count = count_admin_accounts(db)
    enabled_admin_count = count_enabled_admin_accounts(db)

    for user_id in user_ids:
        if user_id in seen_user_ids:
            continue
        seen_user_ids.add(user_id)
        user = db.get(User, user_id)
        if not user:
            failed_items.append({"user_id": user_id, "reason": "用户不存在"})
            continue
        if user.id == acting_admin_id:
            failed_items.append({"user_id": user_id, "reason": "不能删除当前登录管理员账号"})
            continue
        if user.role == "admin":
            if admin_count <= 1:
                failed_items.append({"user_id": user_id, "reason": "系统至少保留一个管理员账号"})
                continue
            if bool(user.is_enabled) and enabled_admin_count <= 1:
                failed_items.append({"user_id": user_id, "reason": "系统必须至少保留一个启用中的管理员账号"})
                continue
        try:
            with db.begin_nested():
                db.delete(user)
                if user.role == "admin":
                    admin_count -= 1
                    if bool(user.is_enabled):
                        enabled_admin_count -= 1
            success_user_ids.append(user_id)
        except Exception as exc:
            failed_items.append({"user_id": user_id, "reason": f"删除失败：{exc}"})

    db.commit()
    return success_user_ids, failed_items


def batch_set_users_enabled(
    db: Session,
    *,
    user_ids: list[int],
    target_enabled: bool,
    acting_admin_id: int,
) -> tuple[list[int], list[dict]]:
    success_user_ids: list[int] = []
    failed_items: list[dict] = []
    seen_user_ids: set[int] = set()

    for user_id in user_ids:
        if user_id in seen_user_ids:
            continue
        seen_user_ids.add(user_id)
        user = db.get(User, user_id)
        if not user:
            failed_items.append({"user_id": user_id, "reason": "用户不存在"})
            continue
        if user.role == "admin":
            failed_items.append({"user_id": user_id, "reason": "管理员账号请在管理员管理页操作"})
            continue
        if not target_enabled and user.id == acting_admin_id:
            failed_items.append({"user_id": user_id, "reason": "不能停用当前登录管理员账号"})
            continue
        try:
            with db.begin_nested():
                user.is_enabled = target_enabled
                db.add(user)
            success_user_ids.append(user_id)
        except Exception as exc:
            failed_items.append({"user_id": user_id, "reason": f"更新失败：{exc}"})

    db.commit()
    return success_user_ids, failed_items


def batch_reset_users_password(
    db: Session,
    *,
    user_ids: list[int],
    new_password: str,
) -> tuple[list[int], list[dict]]:
    success_user_ids: list[int] = []
    failed_items: list[dict] = []
    seen_user_ids: set[int] = set()

    for user_id in user_ids:
        if user_id in seen_user_ids:
            continue
        seen_user_ids.add(user_id)
        user = db.get(User, user_id)
        if not user:
            failed_items.append({"user_id": user_id, "reason": "用户不存在"})
            continue
        if user.role == "admin":
            failed_items.append({"user_id": user_id, "reason": "管理员账号请在管理员管理页操作"})
            continue
        try:
            with db.begin_nested():
                user.password_hash = get_password_hash(new_password)
                user.must_change_password = True
                db.add(user)
            success_user_ids.append(user_id)
        except Exception as exc:
            failed_items.append({"user_id": user_id, "reason": f"重置失败：{exc}"})

    db.commit()
    return success_user_ids, failed_items
