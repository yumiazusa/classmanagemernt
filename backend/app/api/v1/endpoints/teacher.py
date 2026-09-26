from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response

from app.api.deps import CurrentTeacher, DBSession
from app.schemas.teacher import (
    TeacherStudentAccountItem,
    TeacherStudentAccountPage,
    TeacherStudentBatchPasswordResetRequest,
    TeacherStudentBatchPasswordResetResponse,
    TeacherStudentBatchStatusRequest,
    TeacherStudentBatchStatusUpdateResponse,
    TeacherStudentCreateRequest,
    TeacherStudentImportResponse,
    TeacherStudentPasswordResetRequest,
    TeacherStudentPasswordResetResponse,
    TeacherStudentStatusUpdateResponse,
)
from app.services.student_account_exporter import STUDENT_ACCOUNT_EXPORT_FILENAME, build_student_accounts_export_bytes
from app.services.student_importer import import_students_from_excel
from app.services.student_import_template import (
    STUDENT_IMPORT_TEMPLATE_FILENAME,
    build_student_import_template_bytes,
)
from app.services import student_management

router = APIRouter(prefix="/teacher", tags=["teacher"])


def _teacher_scope(db: DBSession, teacher_user: CurrentTeacher) -> student_management.StudentScope:
    return student_management.teacher_student_scope(db, teacher_id=teacher_user.id)


def _handle_sort_validation(sort_by: str, sort_order: str) -> None:
    try:
        student_management.validate_student_list_sort(sort_by, sort_order)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/students", response_model=TeacherStudentAccountPage)
def get_teacher_students(
    db: DBSession,
    teacher_user: CurrentTeacher,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    class_name: str = Query(default=""),
    student_no: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
) -> TeacherStudentAccountPage:
    _handle_sort_validation(sort_by, sort_order)
    data = student_management.list_students(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        class_name=class_name,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
        scope=_teacher_scope(db, teacher_user),
    )
    return TeacherStudentAccountPage(
        items=[TeacherStudentAccountItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.get("/students/class-options", response_model=list[str])
def get_teacher_student_class_options(db: DBSession, teacher_user: CurrentTeacher) -> list[str]:
    return student_management.list_class_options(db, scope=_teacher_scope(db, teacher_user))


@router.post("/students", response_model=TeacherStudentAccountItem, status_code=status.HTTP_201_CREATED)
def create_teacher_student(
    payload: TeacherStudentCreateRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentAccountItem:
    scope = _teacher_scope(db, teacher_user)
    allowed_class_names = set(scope.class_names) if scope.class_names is not None else None
    user, error = student_management.create_student_account(
        db,
        student_no=payload.student_no,
        full_name=payload.full_name,
        class_name=payload.class_name or "",
        password=payload.password,
        allowed_class_names=allowed_class_names,
    )
    if error or not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error or "创建学生失败")
    return TeacherStudentAccountItem(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        student_no=user.student_no,
        class_name=user.class_name,
        role=user.role,
        is_enabled=user.is_enabled,
        created_at=user.created_at,
    )


@router.get("/students/export")
def export_teacher_students(
    db: DBSession,
    teacher_user: CurrentTeacher,
    keyword: str = Query(default=""),
    class_name: str = Query(default=""),
    student_no: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
) -> Response:
    _handle_sort_validation(sort_by, sort_order)
    rows = student_management.list_students_for_export(
        db,
        keyword=keyword,
        class_name=class_name,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
        scope=_teacher_scope(db, teacher_user),
    )
    file_bytes = build_student_accounts_export_bytes(rows)
    encoded_filename = quote(STUDENT_ACCOUNT_EXPORT_FILENAME)
    headers = {
        "Content-Disposition": f'attachment; filename="student_accounts.xlsx"; filename*=UTF-8\'\'{encoded_filename}',
        "Cache-Control": "no-store",
    }
    return Response(content=file_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


@router.post("/students/{user_id}/enable", response_model=TeacherStudentStatusUpdateResponse)
def enable_teacher_student_account(user_id: int, db: DBSession, teacher_user: CurrentTeacher) -> TeacherStudentStatusUpdateResponse:
    user, error = student_management.set_student_enabled(db, user_id=user_id, is_enabled=True, scope=_teacher_scope(db, teacher_user))
    if error or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error or "学生账号不存在")
    return TeacherStudentStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已启用")


@router.post("/students/{user_id}/disable", response_model=TeacherStudentStatusUpdateResponse)
def disable_teacher_student_account(user_id: int, db: DBSession, teacher_user: CurrentTeacher) -> TeacherStudentStatusUpdateResponse:
    user, error = student_management.set_student_enabled(db, user_id=user_id, is_enabled=False, scope=_teacher_scope(db, teacher_user))
    if error or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error or "学生账号不存在")
    return TeacherStudentStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已停用")


@router.post("/students/{user_id}/reset-password", response_model=TeacherStudentPasswordResetResponse)
def reset_teacher_student_password(
    user_id: int,
    payload: TeacherStudentPasswordResetRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentPasswordResetResponse:
    new_password = payload.new_password.strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    user, error = student_management.reset_student_password(db, user_id=user_id, new_password=new_password, scope=_teacher_scope(db, teacher_user))
    if error or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error or "学生账号不存在")
    return TeacherStudentPasswordResetResponse(user_id=user.id, must_change_password=True, message="密码已重置")


@router.post("/students/batch-reset-password", response_model=TeacherStudentBatchPasswordResetResponse)
def batch_reset_teacher_students_password(
    payload: TeacherStudentBatchPasswordResetRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentBatchPasswordResetResponse:
    new_password = payload.new_password.strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    success_user_ids, failed_items = student_management.batch_reset_student_passwords(
        db,
        user_ids=payload.user_ids,
        new_password=new_password,
        scope=_teacher_scope(db, teacher_user),
    )
    return TeacherStudentBatchPasswordResetResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量重置密码完成",
    )


@router.post("/students/batch-enable", response_model=TeacherStudentBatchStatusUpdateResponse)
def batch_enable_teacher_students(
    payload: TeacherStudentBatchStatusRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentBatchStatusUpdateResponse:
    success_user_ids, failed_items = student_management.batch_set_student_enabled(
        db,
        user_ids=payload.user_ids,
        is_enabled=True,
        scope=_teacher_scope(db, teacher_user),
    )
    return TeacherStudentBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量启用完成",
    )


@router.post("/students/batch-disable", response_model=TeacherStudentBatchStatusUpdateResponse)
def batch_disable_teacher_students(
    payload: TeacherStudentBatchStatusRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentBatchStatusUpdateResponse:
    success_user_ids, failed_items = student_management.batch_set_student_enabled(
        db,
        user_ids=payload.user_ids,
        is_enabled=False,
        scope=_teacher_scope(db, teacher_user),
    )
    return TeacherStudentBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量停用完成",
    )


@router.get("/students/import-template")
def download_student_import_template(teacher_user: CurrentTeacher) -> Response:
    _ = teacher_user
    file_bytes = build_student_import_template_bytes()
    encoded_filename = quote(STUDENT_IMPORT_TEMPLATE_FILENAME)
    headers = {
        "Content-Disposition": f'attachment; filename="student_import_template.xlsx"; filename*=UTF-8\'\'{encoded_filename}',
        "Cache-Control": "no-store",
    }
    return Response(content=file_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


@router.post("/students/import", response_model=TeacherStudentImportResponse)
async def import_teacher_students(
    db: DBSession,
    teacher_user: CurrentTeacher,
    file: UploadFile = File(...),
) -> TeacherStudentImportResponse:
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="导入失败：缺少文件名")
    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="导入失败：仅支持 .xlsx 文件")
    file_bytes = await file.read()
    scope = _teacher_scope(db, teacher_user)
    allowed_class_names = set(scope.class_names) if scope.class_names is not None else None
    try:
        result = import_students_from_excel(db, file_bytes=file_bytes, allowed_class_names=allowed_class_names)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"导入失败：{exc}") from exc
    return TeacherStudentImportResponse.model_validate(result)
