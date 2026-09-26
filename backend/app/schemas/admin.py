from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.user import RoleType


class AdminOverviewRead(BaseModel):
    total_users: int
    student_count: int
    teacher_count: int
    admin_count: int
    course_count: int = 0
    experiment_count: int
    enabled_user_count: int
    disabled_user_count: int
    recent_created_users_count: int
    recent_submission_count: int


class AdminUserItem(BaseModel):
    user_id: int
    username: str
    full_name: str | None
    role: RoleType
    student_no: str | None
    class_name: str | None
    is_enabled: bool
    created_at: datetime


class AdminUserPage(BaseModel):
    items: list[AdminUserItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminCreateTeacherRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    full_name: str | None = Field(default=None, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class AdminUserStatusUpdateResponse(BaseModel):
    user_id: int
    is_enabled: bool
    message: str


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)


class AdminResetPasswordResponse(BaseModel):
    user_id: int
    must_change_password: bool
    message: str


class AdminBatchDeleteRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)


class AdminBatchDeleteFailedItem(BaseModel):
    user_id: int
    reason: str


class AdminBatchStatusRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)


class AdminBatchResetPasswordRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)
    new_password: str = Field(min_length=6, max_length=128)


class AdminUserDeleteResponse(BaseModel):
    user_id: int
    message: str


class AdminUserBatchDeleteResponse(BaseModel):
    success_count: int
    failed_count: int
    success_user_ids: list[int]
    failed_items: list[AdminBatchDeleteFailedItem]
    message: str


class AdminUserBatchStatusUpdateResponse(BaseModel):
    success_count: int
    failed_count: int
    success_user_ids: list[int]
    failed_items: list[AdminBatchDeleteFailedItem]
    message: str


class AdminUserBatchResetPasswordResponse(BaseModel):
    success_count: int
    failed_count: int
    success_user_ids: list[int]
    failed_items: list[AdminBatchDeleteFailedItem]
    message: str


class AdminAccountItem(BaseModel):
    user_id: int
    username: str
    full_name: str | None
    role: RoleType
    is_enabled: bool
    must_change_password: bool
    created_at: datetime


class AdminAccountPage(BaseModel):
    items: list[AdminAccountItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminCreateAdminRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    full_name: str | None = Field(default=None, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class AdminAccountStatusUpdateResponse(BaseModel):
    user_id: int
    is_enabled: bool
    message: str


class AdminAccountResetPasswordRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)


class AdminAccountResetPasswordResponse(BaseModel):
    user_id: int
    must_change_password: bool
    message: str


class AdminSetUserRoleRequest(BaseModel):
    role: RoleType


class AdminUserRoleUpdateResponse(BaseModel):
    user_id: int
    role: RoleType
    message: str


class AdminUpdateUserInfoRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    full_name: str | None = Field(default=None, max_length=64)


class AdminUpdateUserInfoResponse(BaseModel):
    user: AdminUserItem
    message: str
