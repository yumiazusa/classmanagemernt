from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentAdmin, DBSession
from app.crud import crud_admin, crud_doc, crud_user
from app.schemas.admin import (
    AdminAccountItem,
    AdminAccountPage,
    AdminAccountResetPasswordRequest,
    AdminAccountResetPasswordResponse,
    AdminAccountStatusUpdateResponse,
    AdminBatchResetPasswordRequest,
    AdminBatchStatusRequest,
    AdminBatchDeleteRequest,
    AdminUserBatchDeleteResponse,
    AdminUserBatchResetPasswordResponse,
    AdminUserBatchStatusUpdateResponse,
    AdminBatchDeleteFailedItem,
    AdminCreateAdminRequest,
    AdminCreateTeacherRequest,
    AdminOverviewRead,
    AdminResetPasswordRequest,
    AdminResetPasswordResponse,
    AdminSetUserRoleRequest,
    AdminUserItem,
    AdminUserDeleteResponse,
    AdminUserPage,
    AdminUserRoleUpdateResponse,
    AdminUserStatusUpdateResponse,
    AdminUpdateUserInfoRequest,
    AdminUpdateUserInfoResponse,
)
from app.schemas.doc import (
    AdminDocCreateRequest,
    AdminDocDeleteResponse,
    AdminDocItemRead,
    AdminDocUpdateRequest,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverviewRead)
def get_admin_overview(db: DBSession, admin_user: CurrentAdmin) -> AdminOverviewRead:
    _ = admin_user
    payload = crud_admin.get_overview_stats(db)
    return AdminOverviewRead.model_validate(payload)


@router.get("/docs", response_model=list[AdminDocItemRead])
def get_admin_docs(
    db: DBSession,
    admin_user: CurrentAdmin,
    keyword: str = Query(default=""),
    category: str = Query(default=""),
) -> list[AdminDocItemRead]:
    _ = admin_user
    items = crud_doc.list_admin_docs(db, keyword=keyword, category=category)
    return [_to_admin_doc_item(item) for item in items]


@router.get("/docs/categories", response_model=list[str])
def get_admin_doc_categories(
    db: DBSession,
    admin_user: CurrentAdmin,
) -> list[str]:
    _ = admin_user
    return crud_doc.list_admin_categories(db)


@router.post("/docs", response_model=AdminDocItemRead, status_code=status.HTTP_201_CREATED)
def create_admin_doc(
    payload: AdminDocCreateRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminDocItemRead:
    _ = admin_user
    create_payload = _clean_doc_payload(payload.model_dump())
    existed = crud_doc.get_by_slug(db, slug=create_payload["slug"])
    if existed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    created = crud_doc.create_doc(db, payload=create_payload)
    return _to_admin_doc_item(created)


@router.put("/docs/{doc_id}", response_model=AdminDocItemRead)
def update_admin_doc(
    doc_id: int,
    payload: AdminDocUpdateRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminDocItemRead:
    _ = admin_user
    doc = crud_doc.get_by_id(db, doc_id=doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    update_payload = payload.model_dump(exclude_unset=True)
    cleaned_payload = _clean_doc_payload(update_payload)
    if "slug" in cleaned_payload:
        existed = crud_doc.get_by_slug_excluding_id(db, slug=cleaned_payload["slug"], exclude_id=doc_id)
        if existed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    updated = crud_doc.update_doc(db, doc=doc, payload=cleaned_payload)
    return _to_admin_doc_item(updated)


@router.delete("/docs/{doc_id}", response_model=AdminDocDeleteResponse)
def delete_admin_doc(
    doc_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminDocDeleteResponse:
    _ = admin_user
    doc = crud_doc.get_by_id(db, doc_id=doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    crud_doc.delete_doc(db, doc=doc)
    return AdminDocDeleteResponse(id=doc_id, message="文档删除成功")


@router.get("/admin-users", response_model=AdminAccountPage)
def get_admin_accounts(
    db: DBSession,
    admin_user: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
) -> AdminAccountPage:
    _ = admin_user
    data = crud_admin.list_admin_accounts(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        is_enabled=is_enabled,
    )
    return AdminAccountPage(
        items=[AdminAccountItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.post("/admin-users", response_model=AdminAccountItem, status_code=status.HTTP_201_CREATED)
def create_admin_account(
    payload: AdminCreateAdminRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminAccountItem:
    _ = admin_user
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名不能为空")
    existed = crud_user.get_by_username(db, username=username)
    if existed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    try:
        created = crud_admin.create_admin_account(
            db,
            username=username,
            full_name=payload.full_name,
            password=payload.password,
        )
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在") from exc
    return AdminAccountItem(
        user_id=created.id,
        username=created.username,
        full_name=created.full_name,
        role=created.role,
        is_enabled=created.is_enabled,
        must_change_password=bool(created.must_change_password),
        created_at=created.created_at,
    )


@router.post("/admin-users/{user_id}/enable", response_model=AdminAccountStatusUpdateResponse)
def enable_admin_account(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminAccountStatusUpdateResponse:
    user, error_message = crud_admin.set_admin_account_enabled(
        db,
        target_user_id=user_id,
        is_enabled=True,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminAccountStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="管理员账号已启用")


@router.post("/admin-users/{user_id}/disable", response_model=AdminAccountStatusUpdateResponse)
def disable_admin_account(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminAccountStatusUpdateResponse:
    user, error_message = crud_admin.set_admin_account_enabled(
        db,
        target_user_id=user_id,
        is_enabled=False,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminAccountStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="管理员账号已停用")


@router.post("/admin-users/{user_id}/reset-password", response_model=AdminAccountResetPasswordResponse)
def reset_admin_account_password(
    user_id: int,
    payload: AdminAccountResetPasswordRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminAccountResetPasswordResponse:
    _ = admin_user
    cleaned_password = payload.new_password.strip()
    if len(cleaned_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    user, error_message = crud_admin.reset_admin_account_password(
        db,
        target_user_id=user_id,
        new_password=cleaned_password,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminAccountResetPasswordResponse(
        user_id=user.id,
        must_change_password=bool(user.must_change_password),
        message="管理员密码重置成功",
    )


@router.get("/users", response_model=AdminUserPage)
def get_admin_users(
    db: DBSession,
    admin_user: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    role_filter: str = Query(default="all", alias="role"),
    class_name: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
) -> AdminUserPage:
    _ = admin_user
    if role_filter not in {"all", "student", "teacher", "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role 参数仅支持 all/student/teacher/admin")
    data = crud_admin.list_users(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        role_filter=role_filter,
        class_name=class_name,
        is_enabled=is_enabled,
    )
    return AdminUserPage(
        items=[AdminUserItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.get("/users/class-options", response_model=list[str])
def get_admin_user_class_options(
    db: DBSession,
    admin_user: CurrentAdmin,
) -> list[str]:
    _ = admin_user
    return crud_admin.list_user_class_options(db)


@router.post("/teachers", response_model=AdminUserItem, status_code=status.HTTP_201_CREATED)
def create_admin_teacher(
    payload: AdminCreateTeacherRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserItem:
    _ = admin_user
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名不能为空")
    existed = crud_user.get_by_username(db, username=username)
    if existed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    try:
        created = crud_admin.create_teacher(
            db,
            username=username,
            full_name=payload.full_name,
            password=payload.password,
        )
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在") from exc
    return AdminUserItem(
        user_id=created.id,
        username=created.username,
        full_name=created.full_name,
        role=created.role,
        student_no=created.student_no,
        class_name=created.class_name,
        is_enabled=created.is_enabled,
        created_at=created.created_at,
    )


@router.post("/users/{user_id}/enable", response_model=AdminUserStatusUpdateResponse)
def enable_admin_user(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserStatusUpdateResponse:
    user, error_message = crud_admin.set_user_enabled(
        db,
        target_user_id=user_id,
        is_enabled=True,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminUserStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已启用")


@router.post("/users/{user_id}/disable", response_model=AdminUserStatusUpdateResponse)
def disable_admin_user(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserStatusUpdateResponse:
    user, error_message = crud_admin.set_user_enabled(
        db,
        target_user_id=user_id,
        is_enabled=False,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminUserStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已停用")


@router.post("/users/{user_id}/reset-password", response_model=AdminResetPasswordResponse)
def reset_admin_user_password(
    user_id: int,
    payload: AdminResetPasswordRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminResetPasswordResponse:
    _ = admin_user
    cleaned_password = payload.new_password.strip()
    if len(cleaned_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    user, error_message = crud_admin.reset_user_password(
        db,
        target_user_id=user_id,
        new_password=cleaned_password,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminResetPasswordResponse(
        user_id=user.id,
        must_change_password=bool(user.must_change_password),
        message="密码重置成功",
    )


@router.post("/users/{user_id}/set-role", response_model=AdminUserRoleUpdateResponse)
def set_admin_user_role(
    user_id: int,
    payload: AdminSetUserRoleRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserRoleUpdateResponse:
    user, error_message = crud_admin.set_user_role(
        db,
        target_user_id=user_id,
        target_role=payload.role,
        acting_admin_id=admin_user.id,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminUserRoleUpdateResponse(user_id=user.id, role=user.role, message="角色设置成功")


@router.post("/users/{user_id}/update-info", response_model=AdminUpdateUserInfoResponse)
def update_admin_user_info(
    user_id: int,
    payload: AdminUpdateUserInfoRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUpdateUserInfoResponse:
    _ = admin_user
    user, error_message = crud_admin.update_user_basic_info(
        db,
        target_user_id=user_id,
        username=payload.username,
        full_name=payload.full_name,
    )
    if not user:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "操作失败")
    return AdminUpdateUserInfoResponse(
        message="用户信息更新成功",
        user=AdminUserItem(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            student_no=user.student_no,
            class_name=user.class_name,
            is_enabled=user.is_enabled,
            created_at=user.created_at,
        ),
    )


@router.post("/users/{user_id}/delete", response_model=AdminUserDeleteResponse)
def delete_admin_user(
    user_id: int,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserDeleteResponse:
    success, error_message = crud_admin.delete_user(
        db,
        target_user_id=user_id,
        acting_admin_id=admin_user.id,
    )
    if not success:
        if error_message == "用户不存在":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message or "删除失败")
    return AdminUserDeleteResponse(user_id=user_id, message="账号删除成功")


@router.post("/users/batch-delete", response_model=AdminUserBatchDeleteResponse)
def batch_delete_admin_users(
    payload: AdminBatchDeleteRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserBatchDeleteResponse:
    success_user_ids, failed_items = crud_admin.batch_delete_users(
        db,
        user_ids=payload.user_ids,
        acting_admin_id=admin_user.id,
    )
    return AdminUserBatchDeleteResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=[AdminBatchDeleteFailedItem.model_validate(item) for item in failed_items],
        message="批量删除完成",
    )


@router.post("/users/batch-enable", response_model=AdminUserBatchStatusUpdateResponse)
def batch_enable_admin_users(
    payload: AdminBatchStatusRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserBatchStatusUpdateResponse:
    success_user_ids, failed_items = crud_admin.batch_set_users_enabled(
        db,
        user_ids=payload.user_ids,
        target_enabled=True,
        acting_admin_id=admin_user.id,
    )
    return AdminUserBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=[AdminBatchDeleteFailedItem.model_validate(item) for item in failed_items],
        message="批量启用完成",
    )


@router.post("/users/batch-disable", response_model=AdminUserBatchStatusUpdateResponse)
def batch_disable_admin_users(
    payload: AdminBatchStatusRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserBatchStatusUpdateResponse:
    success_user_ids, failed_items = crud_admin.batch_set_users_enabled(
        db,
        user_ids=payload.user_ids,
        target_enabled=False,
        acting_admin_id=admin_user.id,
    )
    return AdminUserBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=[AdminBatchDeleteFailedItem.model_validate(item) for item in failed_items],
        message="批量停用完成",
    )


@router.post("/users/batch-reset-password", response_model=AdminUserBatchResetPasswordResponse)
def batch_reset_admin_users_password(
    payload: AdminBatchResetPasswordRequest,
    db: DBSession,
    admin_user: CurrentAdmin,
) -> AdminUserBatchResetPasswordResponse:
    _ = admin_user
    new_password = payload.new_password.strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")
    success_user_ids, failed_items = crud_admin.batch_reset_users_password(
        db,
        user_ids=payload.user_ids,
        new_password=new_password,
    )
    return AdminUserBatchResetPasswordResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=[AdminBatchDeleteFailedItem.model_validate(item) for item in failed_items],
        message="批量重置密码完成",
    )
