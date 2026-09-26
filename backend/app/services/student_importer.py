from io import BytesIO

import pandas as pd
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.models.course import ClassGroup
from app.services import student_management

REQUIRED_COLUMNS = ("班级", "学号", "姓名")
DEFAULT_PASSWORD = "123456"


def _normalize_header(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return text.replace(" ", "")


def _normalize_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def _get_or_create_class_group(db: Session, class_name: str) -> ClassGroup:
    class_group = db.query(ClassGroup).filter(ClassGroup.name == class_name).first()
    if class_group:
        return class_group
    class_group = ClassGroup(name=class_name, is_active=True)
    db.add(class_group)
    db.flush()
    return class_group


def _ensure_class_member(db: Session, *, class_group_id: int, user_id: int) -> None:
    student_management.ensure_class_member(db, class_group_id=class_group_id, user_id=user_id)


def import_students_from_excel(
    db: Session,
    file_bytes: bytes,
    *,
    forced_class_name: str | None = None,
    forced_class_group_id: int | None = None,
    allowed_class_names: set[str] | None = None,
) -> dict:
    if not file_bytes:
        raise ValueError("导入失败：文件为空")
    try:
        dataframe = pd.read_excel(BytesIO(file_bytes), dtype=str)
    except Exception as exc:
        raise ValueError(f"导入失败：无法解析 Excel 文件（{exc}）") from exc

    normalized_column_map: dict[str, str] = {}
    for column in dataframe.columns.tolist():
        normalized = _normalize_header(column)
        if normalized and normalized not in normalized_column_map:
            normalized_column_map[normalized] = column

    required_columns = ("学号", "姓名") if forced_class_name else REQUIRED_COLUMNS
    missing_columns = [column for column in required_columns if column not in normalized_column_map]
    if missing_columns:
        missing_text = "、".join(f"【{name}】" for name in missing_columns)
        raise ValueError(f"导入失败：缺少必要列{missing_text}")

    class_column = normalized_column_map.get("班级")
    student_no_column = normalized_column_map["学号"]
    full_name_column = normalized_column_map["姓名"]

    records = dataframe.to_dict(orient="records")
    total_rows = len(records)
    created_count = 0
    updated_count = 0
    skipped_count = 0
    failed_items: list[dict] = []
    seen_student_nos: set[str] = set()

    for index, row in enumerate(records, start=2):
        class_name = forced_class_name or _normalize_cell(row.get(class_column))
        student_no = _normalize_cell(row.get(student_no_column))
        full_name = _normalize_cell(row.get(full_name_column))

        if not class_name:
            skipped_count += 1
            failed_items.append({"row": index, "student_no": student_no, "reason": "班级为空"})
            continue
        if allowed_class_names is not None and class_name not in allowed_class_names:
            skipped_count += 1
            failed_items.append({"row": index, "student_no": student_no, "reason": "班级不在当前管理范围内"})
            continue
        if not student_no:
            skipped_count += 1
            failed_items.append({"row": index, "student_no": "", "reason": "学号为空"})
            continue
        if not full_name:
            skipped_count += 1
            failed_items.append({"row": index, "student_no": student_no, "reason": "姓名为空"})
            continue
        if student_no in seen_student_nos:
            skipped_count += 1
            failed_items.append({"row": index, "student_no": student_no, "reason": "文件内学号重复"})
            continue
        seen_student_nos.add(student_no)

        try:
            with db.begin_nested():
                existed_by_student_no = crud_user.get_by_student_no(db, student_no=student_no)
                if existed_by_student_no:
                    existed_by_student_no.class_name = class_name
                    existed_by_student_no.full_name = full_name
                    db.add(existed_by_student_no)
                    class_group = db.get(ClassGroup, forced_class_group_id) if forced_class_group_id else _get_or_create_class_group(db, class_name)
                    _ensure_class_member(db, class_group_id=class_group.id, user_id=existed_by_student_no.id)
                    updated_count += 1
                    continue

                existed_by_username = crud_user.get_by_username(db, username=student_no)
                if existed_by_username:
                    if existed_by_username.role != "student":
                        skipped_count += 1
                        failed_items.append(
                            {"row": index, "student_no": student_no, "reason": "同名账号已存在且角色不是学生"}
                        )
                        continue
                    if existed_by_username.student_no and existed_by_username.student_no != student_no:
                        skipped_count += 1
                        failed_items.append(
                            {"row": index, "student_no": student_no, "reason": "同名账号已绑定其他学号"}
                        )
                        continue
                    existed_by_username.student_no = student_no
                    existed_by_username.class_name = class_name
                    existed_by_username.full_name = full_name
                    db.add(existed_by_username)
                    class_group = db.get(ClassGroup, forced_class_group_id) if forced_class_group_id else _get_or_create_class_group(db, class_name)
                    _ensure_class_member(db, class_group_id=class_group.id, user_id=existed_by_username.id)
                    updated_count += 1
                    continue

                created = crud_user.create_student_by_import(
                    db,
                    username=student_no,
                    student_no=student_no,
                    class_name=class_name,
                    full_name=full_name,
                    default_password=DEFAULT_PASSWORD,
                )
                class_group = db.get(ClassGroup, forced_class_group_id) if forced_class_group_id else _get_or_create_class_group(db, class_name)
                _ensure_class_member(db, class_group_id=class_group.id, user_id=created.id)
                created_count += 1
        except Exception as exc:
            skipped_count += 1
            failed_items.append({"row": index, "student_no": student_no, "reason": f"导入异常：{exc}"})

    db.commit()
    return {
        "total_rows": total_rows,
        "created_count": created_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "failed_items": failed_items,
        "message": "导入完成",
    }
