from math import ceil
from typing import NamedTuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.course import ClassGroup, ClassMember, CourseClass, CourseTeacher
from app.models.user import User

ALLOWED_STUDENT_SORT_BY = {"created_at", "username", "full_name", "student_no", "class_name", "is_enabled"}
ALLOWED_SORT_ORDER = {"asc", "desc"}


class StudentScope(NamedTuple):
    class_group_ids: list[int] | None = None
    class_names: list[str] | None = None


def teacher_student_scope(db: Session, *, teacher_id: int) -> StudentScope:
    statement = (
        select(ClassGroup.id, ClassGroup.name)
        .join(CourseClass, CourseClass.class_group_id == ClassGroup.id)
        .join(CourseTeacher, CourseTeacher.course_id == CourseClass.course_id)
        .where(CourseTeacher.teacher_id == teacher_id)
        .distinct()
    )
    rows = db.execute(statement).all()
    if not rows:
        return StudentScope(class_group_ids=None, class_names=None)
    return StudentScope(
        class_group_ids=[int(row.id) for row in rows],
        class_names=[row.name for row in rows if row.name],
    )


def class_scope(class_group: ClassGroup) -> StudentScope:
    return StudentScope(class_group_ids=[class_group.id], class_names=[class_group.name])


def _get_or_create_class_group(db: Session, class_name: str) -> ClassGroup:
    class_group = db.query(ClassGroup).filter(ClassGroup.name == class_name).first()
    if class_group:
        return class_group
    class_group = ClassGroup(name=class_name, is_active=True)
    db.add(class_group)
    db.flush()
    return class_group


def ensure_class_member(db: Session, *, class_group_id: int, user_id: int) -> None:
    exists = (
        db.query(ClassMember.id)
        .filter(ClassMember.class_group_id == class_group_id, ClassMember.user_id == user_id)
        .first()
    )
    if not exists:
        db.add(ClassMember(class_group_id=class_group_id, user_id=user_id))


def create_student_account(
    db: Session,
    *,
    student_no: str,
    full_name: str,
    class_name: str,
    password: str = "123456",
    forced_class_group_id: int | None = None,
    allowed_class_names: set[str] | None = None,
) -> tuple[User | None, str | None]:
    clean_student_no = student_no.strip()
    clean_full_name = full_name.strip()
    clean_class_name = class_name.strip()
    clean_password = password.strip()
    if not clean_student_no:
        return None, "学号不能为空"
    if not clean_full_name:
        return None, "姓名不能为空"
    if not clean_class_name:
        return None, "班级不能为空"
    if len(clean_password) < 6:
        return None, "初始密码长度不能少于 6 位"
    if allowed_class_names is not None and clean_class_name not in allowed_class_names:
        return None, "班级不在当前管理范围内"
    if db.execute(select(User.id).where(User.student_no == clean_student_no)).first():
        return None, "学号已存在"
    if db.execute(select(User.id).where(User.username == clean_student_no)).first():
        return None, "同名账号已存在"

    class_group = db.get(ClassGroup, forced_class_group_id) if forced_class_group_id else _get_or_create_class_group(db, clean_class_name)
    if not class_group:
        return None, "班级不存在"
    user = User(
        username=clean_student_no,
        password_hash=get_password_hash(clean_password),
        role="student",
        must_change_password=True,
        student_no=clean_student_no,
        class_name=clean_class_name,
        full_name=clean_full_name,
    )
    db.add(user)
    db.flush()
    ensure_class_member(db, class_group_id=class_group.id, user_id=user.id)
    db.commit()
    db.refresh(user)
    return user, None


def validate_student_list_sort(sort_by: str, sort_order: str) -> None:
    if sort_by not in ALLOWED_STUDENT_SORT_BY:
        raise ValueError("sort_by 参数仅支持 created_at/username/full_name/student_no/class_name/is_enabled")
    if sort_order not in ALLOWED_SORT_ORDER:
        raise ValueError("sort_order 参数仅支持 asc/desc")


def _scope_condition(scope: StudentScope | None):
    if not scope:
        return None
    conditions = []
    if scope.class_names is not None:
        if len(scope.class_names) == 0:
            return False
        conditions.append(User.class_name.in_(scope.class_names))
    if scope.class_group_ids is not None:
        if len(scope.class_group_ids) == 0:
            return False
        conditions.append(ClassMember.class_group_id.in_(scope.class_group_ids))
    if not conditions:
        return None
    return or_(*conditions)


def _student_statement(
    *,
    keyword: str = "",
    class_name: str = "",
    student_no: str = "",
    is_enabled: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    scope: StudentScope | None = None,
):
    statement = (
        select(
            User.id.label("user_id"),
            User.username,
            User.full_name,
            User.student_no,
            User.class_name,
            User.role,
            User.is_enabled,
            User.created_at,
        )
        .select_from(User)
        .outerjoin(ClassMember, ClassMember.user_id == User.id)
        .where(User.role == "student")
        .distinct()
    )

    scope_condition = _scope_condition(scope)
    if scope_condition is False:
        statement = statement.where(False)
    elif scope_condition is not None:
        statement = statement.where(scope_condition)

    clean_keyword = keyword.strip()
    if clean_keyword:
        statement = statement.where(
            or_(
                User.username.ilike(f"%{clean_keyword}%"),
                User.full_name.ilike(f"%{clean_keyword}%"),
                User.student_no.ilike(f"%{clean_keyword}%"),
            )
        )
    if class_name.strip():
        statement = statement.where(User.class_name.ilike(f"%{class_name.strip()}%"))
    if student_no.strip():
        statement = statement.where(User.student_no.ilike(f"%{student_no.strip()}%"))
    if is_enabled is not None:
        statement = statement.where(User.is_enabled == is_enabled)

    sort_mapping = {
        "created_at": User.created_at,
        "username": User.username,
        "full_name": User.full_name,
        "student_no": User.student_no,
        "class_name": User.class_name,
        "is_enabled": User.is_enabled,
    }
    sort_column = sort_mapping.get(sort_by, User.created_at)
    return statement.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc(), User.id.asc())


def _map_student_row(row) -> dict:
    return {
        "user_id": row.user_id,
        "username": row.username,
        "full_name": row.full_name,
        "student_no": row.student_no,
        "class_name": row.class_name,
        "role": row.role,
        "is_enabled": bool(row.is_enabled),
        "created_at": row.created_at,
    }


def list_students(
    db: Session,
    *,
    page: int,
    page_size: int,
    keyword: str = "",
    class_name: str = "",
    student_no: str = "",
    is_enabled: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    scope: StudentScope | None = None,
) -> dict:
    validate_student_list_sort(sort_by, sort_order)
    statement = _student_statement(
        keyword=keyword,
        class_name=class_name,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
        scope=scope,
    )
    total = int(db.execute(select(func.count()).select_from(statement.subquery())).scalar_one() or 0)
    total_pages = ceil(total / page_size) if total > 0 else 0
    rows = db.execute(statement.offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [_map_student_row(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def list_students_for_export(db: Session, *, scope: StudentScope | None = None, **kwargs) -> list[dict]:
    validate_student_list_sort(kwargs.get("sort_by", "created_at"), kwargs.get("sort_order", "desc"))
    statement = _student_statement(scope=scope, **kwargs)
    return [_map_student_row(row) for row in db.execute(statement).all()]


def list_class_options(db: Session, *, scope: StudentScope | None = None) -> list[str]:
    class_group_statement = select(ClassGroup.name).where(ClassGroup.name.is_not(None), ClassGroup.name != "")
    if scope and scope.class_group_ids is not None:
        if len(scope.class_group_ids) == 0:
            return []
        class_group_statement = class_group_statement.where(ClassGroup.id.in_(scope.class_group_ids))
    class_group_names = db.execute(class_group_statement).scalars().all()

    user_statement = (
        select(User.class_name)
        .select_from(User)
        .outerjoin(ClassMember, ClassMember.user_id == User.id)
        .where(User.role == "student", User.class_name.is_not(None), User.class_name != "")
    )
    scope_condition = _scope_condition(scope)
    if scope_condition is False:
        return sorted({item for item in class_group_names if isinstance(item, str) and item.strip()})
    if scope_condition is not None:
        user_statement = user_statement.where(scope_condition)
    rows = db.execute(user_statement.group_by(User.class_name)).scalars().all()
    return sorted({item for item in [*class_group_names, *rows] if isinstance(item, str) and item.strip()})


def student_in_scope(db: Session, *, user_id: int, scope: StudentScope | None = None) -> User | None:
    statement = select(User).outerjoin(ClassMember, ClassMember.user_id == User.id).where(User.id == user_id, User.role == "student")
    scope_condition = _scope_condition(scope)
    if scope_condition is False:
        return None
    if scope_condition is not None:
        statement = statement.where(scope_condition)
    return db.execute(statement.distinct()).scalar_one_or_none()


def set_student_enabled(db: Session, *, user_id: int, is_enabled: bool, scope: StudentScope | None = None) -> tuple[User | None, str | None]:
    user = student_in_scope(db, user_id=user_id, scope=scope)
    if not user:
        return None, "学生不存在或不在当前管理范围内"
    user.is_enabled = is_enabled
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def reset_student_password(db: Session, *, user_id: int, new_password: str, scope: StudentScope | None = None) -> tuple[User | None, str | None]:
    user = student_in_scope(db, user_id=user_id, scope=scope)
    if not user:
        return None, "学生不存在或不在当前管理范围内"
    user.password_hash = get_password_hash(new_password)
    user.must_change_password = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def batch_set_student_enabled(
    db: Session,
    *,
    user_ids: list[int],
    is_enabled: bool,
    scope: StudentScope | None = None,
) -> tuple[list[int], list[dict]]:
    success_user_ids: list[int] = []
    failed_items: list[dict] = []
    for user_id in dict.fromkeys(user_ids):
        user = student_in_scope(db, user_id=user_id, scope=scope)
        if not user:
            failed_items.append({"user_id": user_id, "reason": "学生不存在或不在当前管理范围内"})
            continue
        user.is_enabled = is_enabled
        db.add(user)
        success_user_ids.append(user_id)
    db.commit()
    return success_user_ids, failed_items


def batch_reset_student_passwords(
    db: Session,
    *,
    user_ids: list[int],
    new_password: str,
    scope: StudentScope | None = None,
) -> tuple[list[int], list[dict]]:
    success_user_ids: list[int] = []
    failed_items: list[dict] = []
    password_hash = get_password_hash(new_password)
    for user_id in dict.fromkeys(user_ids):
        user = student_in_scope(db, user_id=user_id, scope=scope)
        if not user:
            failed_items.append({"user_id": user_id, "reason": "学生不存在或不在当前管理范围内"})
            continue
        user.password_hash = password_hash
        user.must_change_password = True
        db.add(user)
        success_user_ids.append(user_id)
    db.commit()
    return success_user_ids, failed_items
