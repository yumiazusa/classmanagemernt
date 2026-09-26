from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response

from app.api.deps import CurrentAdmin, DBSession
from app.crud import crud_course
from app.models.course import ClassGroup
from app.schemas.course import (
    ClassGroupCreate,
    ClassGroupPage,
    ClassGroupRead,
    ClassGroupUpdate,
    CourseCreate,
    CourseModuleCreate,
    CourseModuleRead,
    CoursePage,
    CourseRead,
    CourseTaskCreate,
    CourseTaskRead,
    CourseTaskUpdate,
    CourseUpdate,
)
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
from app.services import student_management
from app.services.student_account_exporter import STUDENT_ACCOUNT_EXPORT_FILENAME, build_student_accounts_export_bytes
from app.services.student_importer import import_students_from_excel
from app.services.student_import_template import STUDENT_IMPORT_TEMPLATE_FILENAME, build_student_import_template_bytes

router = APIRouter(prefix="/admin", tags=["admin-courses"])


def _get_class_or_404(db: DBSession, class_id: int) -> ClassGroup:
    class_group = db.get(ClassGroup, class_id)
    if not class_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")
    return class_group


def _class_student_scope(class_group: ClassGroup) -> student_management.StudentScope:
    return student_management.class_scope(class_group)


def _handle_sort_validation(sort_by: str, sort_order: str) -> None:
    try:
        student_management.validate_student_list_sort(sort_by, sort_order)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/courses", response_model=CoursePage)
def list_admin_courses(
    db: DBSession,
    admin_user: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status_filter: str = Query(default="all", alias="status"),
) -> CoursePage:
    _ = admin_user
    data = crud_course.list_admin_courses(db, page=page, page_size=page_size, keyword=keyword, status=status_filter)
    return CoursePage(**data)


@router.post("/courses", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_admin_course(payload: CourseCreate, db: DBSession, admin_user: CurrentAdmin) -> CourseRead:
    _ = admin_user
    if crud_course.get_course_by_slug(db, payload.slug.strip()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    created = crud_course.create_course(db, payload.model_dump())
    item = crud_course.get_course_read(db, course_id=created.id)
    return CourseRead.model_validate(item)


@router.get("/courses/{course_id}", response_model=CourseRead)
def get_admin_course(course_id: int, db: DBSession, admin_user: CurrentAdmin) -> CourseRead:
    _ = admin_user
    item = crud_course.get_course_read(db, course_id=course_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    return CourseRead.model_validate(item)


@router.put("/courses/{course_id}", response_model=CourseRead)
def update_admin_course(course_id: int, payload: CourseUpdate, db: DBSession, admin_user: CurrentAdmin) -> CourseRead:
    _ = admin_user
    course = crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    update_payload = payload.model_dump(exclude_unset=True)
    if "slug" in update_payload:
        existed = crud_course.get_course_by_slug(db, update_payload["slug"].strip())
        if existed and existed.id != course_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    crud_course.update_course(db, course, update_payload)
    item = crud_course.get_course_read(db, course_id=course_id)
    return CourseRead.model_validate(item)


@router.delete("/courses/{course_id}")
def delete_admin_course(course_id: int, db: DBSession, admin_user: CurrentAdmin) -> dict:
    _ = admin_user
    course = crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    crud_course.delete_course(db, course)
    return {"course_id": course_id, "message": "课程已删除"}


@router.post("/courses/{course_id}/modules", response_model=CourseModuleRead, status_code=status.HTTP_201_CREATED)
def create_admin_module(course_id: int, payload: CourseModuleCreate, db: DBSession, admin_user: CurrentAdmin) -> CourseModuleRead:
    _ = admin_user
    if course_id != payload.course_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="course_id 不一致")
    created = crud_course.create_module(db, payload.model_dump())
    item = crud_course.list_modules(db, course_id=course_id, include_unpublished=True)[-1]
    item["id"] = created.id
    return CourseModuleRead.model_validate(item)


@router.post("/courses/{course_id}/tasks", response_model=CourseTaskRead, status_code=status.HTTP_201_CREATED)
def create_admin_task(course_id: int, payload: CourseTaskCreate, db: DBSession, admin_user: CurrentAdmin) -> CourseTaskRead:
    _ = admin_user
    if course_id != payload.course_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="course_id 不一致")
    created = crud_course.create_task(db, payload.model_dump())
    item = crud_course.get_task_read(db, task_id=created.id)
    return CourseTaskRead.model_validate(item)


@router.put("/tasks/{task_id}", response_model=CourseTaskRead)
def update_admin_task(task_id: int, payload: CourseTaskUpdate, db: DBSession, admin_user: CurrentAdmin) -> CourseTaskRead:
    _ = admin_user
    from app.models.course import CourseTask

    task = db.get(CourseTask, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    crud_course.update_task(db, task, payload.model_dump(exclude_unset=True))
    item = crud_course.get_task_read(db, task_id=task_id)
    return CourseTaskRead.model_validate(item)


@router.get("/classes", response_model=ClassGroupPage)
def list_admin_classes(
    db: DBSession,
    admin_user: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
) -> ClassGroupPage:
    _ = admin_user
    crud_course.sync_class_members_from_user_class_names(db)
    data = crud_course.list_classes(db, page=page, page_size=page_size, keyword=keyword)
    return ClassGroupPage(**data)


@router.post("/classes", response_model=ClassGroupRead, status_code=status.HTTP_201_CREATED)
def create_admin_class(payload: ClassGroupCreate, db: DBSession, admin_user: CurrentAdmin) -> ClassGroupRead:
    _ = admin_user
    existed = db.query(ClassGroup).filter(ClassGroup.name == payload.name.strip()).first()
    if existed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="班级名称已存在")
    created = crud_course.create_class(db, payload.model_dump())
    return ClassGroupRead.model_validate({**created.__dict__, "member_count": 0, "course_count": 0})


@router.get("/classes/{class_id}", response_model=ClassGroupRead)
def get_admin_class(class_id: int, db: DBSession, admin_user: CurrentAdmin) -> ClassGroupRead:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    data = crud_course.list_classes(db, page=1, page_size=1, keyword=class_group.name)
    item = next((row for row in data["items"] if row["id"] == class_group.id), None)
    if item:
        return ClassGroupRead.model_validate(item)
    return ClassGroupRead.model_validate({**class_group.__dict__, "member_count": 0, "course_count": 0})


@router.put("/classes/{class_id}", response_model=ClassGroupRead)
def update_admin_class(class_id: int, payload: ClassGroupUpdate, db: DBSession, admin_user: CurrentAdmin) -> ClassGroupRead:
    _ = admin_user
    class_group = db.get(ClassGroup, class_id)
    if not class_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(class_group, key, value.strip() if isinstance(value, str) else value)
    db.add(class_group)
    db.commit()
    db.refresh(class_group)
    return ClassGroupRead.model_validate({**class_group.__dict__, "member_count": 0, "course_count": 0})


@router.get("/classes/{class_id}/students", response_model=TeacherStudentAccountPage)
def get_admin_class_students(
    class_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    student_no: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
) -> TeacherStudentAccountPage:
    _ = admin_user
    _handle_sort_validation(sort_by, sort_order)
    class_group = _get_class_or_404(db, class_id)
    data = student_management.list_students(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
        scope=_class_student_scope(class_group),
    )
    return TeacherStudentAccountPage(
        items=[TeacherStudentAccountItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.post("/classes/{class_id}/students", response_model=TeacherStudentAccountItem, status_code=status.HTTP_201_CREATED)
def create_admin_class_student(
    class_id: int,
    payload: TeacherStudentCreateRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> TeacherStudentAccountItem:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    user, error = student_management.create_student_account(
        db,
        student_no=payload.student_no,
        full_name=payload.full_name,
        class_name=class_group.name,
        password=payload.password,
        forced_class_group_id=class_group.id,
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


@router.get("/classes/{class_id}/students/export")
def export_admin_class_students(
    class_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
    keyword: str = Query(default=""),
    student_no: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
) -> Response:
    _ = admin_user
    _handle_sort_validation(sort_by, sort_order)
    class_group = _get_class_or_404(db, class_id)
    rows = student_management.list_students_for_export(
        db,
        keyword=keyword,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
        scope=_class_student_scope(class_group),
    )
    file_bytes = build_student_accounts_export_bytes(rows)
    encoded_filename = quote(STUDENT_ACCOUNT_EXPORT_FILENAME)
    headers = {
        "Content-Disposition": f'attachment; filename="student_accounts.xlsx"; filename*=UTF-8\'\'{encoded_filename}',
        "Cache-Control": "no-store",
    }
    return Response(content=file_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


@router.get("/classes/{class_id}/students/import-template")
def download_admin_class_student_import_template(
    class_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> Response:
    _ = admin_user
    _get_class_or_404(db, class_id)
    file_bytes = build_student_import_template_bytes()
    encoded_filename = quote(STUDENT_IMPORT_TEMPLATE_FILENAME)
    headers = {
        "Content-Disposition": f'attachment; filename="student_import_template.xlsx"; filename*=UTF-8\'\'{encoded_filename}',
        "Cache-Control": "no-store",
    }
    return Response(content=file_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


@router.post("/classes/{class_id}/students/import", response_model=TeacherStudentImportResponse)
async def import_admin_class_students(
    class_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
    file: UploadFile = File(...),
) -> TeacherStudentImportResponse:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="导入失败：缺少文件名")
    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="导入失败：仅支持 .xlsx 文件")
    file_bytes = await file.read()
    try:
        result = import_students_from_excel(
            db,
            file_bytes=file_bytes,
            forced_class_name=class_group.name,
            forced_class_group_id=class_group.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"导入失败：{exc}") from exc
    return TeacherStudentImportResponse.model_validate(result)


@router.post("/classes/{class_id}/students/{user_id}/enable", response_model=TeacherStudentStatusUpdateResponse)
def enable_admin_class_student(
    class_id: int,
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> TeacherStudentStatusUpdateResponse:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    user, error = student_management.set_student_enabled(db, user_id=user_id, is_enabled=True, scope=_class_student_scope(class_group))
    if error or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error or "学生账号不存在")
    return TeacherStudentStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已启用")


@router.post("/classes/{class_id}/students/{user_id}/disable", response_model=TeacherStudentStatusUpdateResponse)
def disable_admin_class_student(
    class_id: int,
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> TeacherStudentStatusUpdateResponse:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    user, error = student_management.set_student_enabled(db, user_id=user_id, is_enabled=False, scope=_class_student_scope(class_group))
    if error or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error or "学生账号不存在")
    return TeacherStudentStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已停用")


@router.post("/classes/{class_id}/students/{user_id}/reset-password", response_model=TeacherStudentPasswordResetResponse)
def reset_admin_class_student_password(
    class_id: int,
    user_id: int,
    payload: TeacherStudentPasswordResetRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> TeacherStudentPasswordResetResponse:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    new_password = payload.new_password.strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    user, error = student_management.reset_student_password(
        db,
        user_id=user_id,
        new_password=new_password,
        scope=_class_student_scope(class_group),
    )
    if error or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error or "学生账号不存在")
    return TeacherStudentPasswordResetResponse(user_id=user.id, must_change_password=True, message="密码已重置")


@router.post("/classes/{class_id}/students/batch-reset-password", response_model=TeacherStudentBatchPasswordResetResponse)
def batch_reset_admin_class_students_password(
    class_id: int,
    payload: TeacherStudentBatchPasswordResetRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> TeacherStudentBatchPasswordResetResponse:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    new_password = payload.new_password.strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    success_user_ids, failed_items = student_management.batch_reset_student_passwords(
        db,
        user_ids=payload.user_ids,
        new_password=new_password,
        scope=_class_student_scope(class_group),
    )
    return TeacherStudentBatchPasswordResetResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量重置密码完成",
    )


@router.post("/classes/{class_id}/students/batch-enable", response_model=TeacherStudentBatchStatusUpdateResponse)
def batch_enable_admin_class_students(
    class_id: int,
    payload: TeacherStudentBatchStatusRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> TeacherStudentBatchStatusUpdateResponse:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    success_user_ids, failed_items = student_management.batch_set_student_enabled(
        db,
        user_ids=payload.user_ids,
        is_enabled=True,
        scope=_class_student_scope(class_group),
    )
    return TeacherStudentBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量启用完成",
    )


@router.post("/classes/{class_id}/students/batch-disable", response_model=TeacherStudentBatchStatusUpdateResponse)
def batch_disable_admin_class_students(
    class_id: int,
    payload: TeacherStudentBatchStatusRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> TeacherStudentBatchStatusUpdateResponse:
    _ = admin_user
    class_group = _get_class_or_404(db, class_id)
    success_user_ids, failed_items = student_management.batch_set_student_enabled(
        db,
        user_ids=payload.user_ids,
        is_enabled=False,
        scope=_class_student_scope(class_group),
    )
    return TeacherStudentBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量停用完成",
    )
