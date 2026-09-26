from datetime import datetime

from pydantic import BaseModel, Field


class TeacherStudentImportFailedItem(BaseModel):
    row: int
    student_no: str
    reason: str


class TeacherStudentImportResponse(BaseModel):
    total_rows: int
    created_count: int
    updated_count: int
    skipped_count: int
    failed_items: list[TeacherStudentImportFailedItem]
    message: str


class TeacherStudentCreateRequest(BaseModel):
    student_no: str = Field(min_length=1, max_length=32)
    full_name: str = Field(min_length=1, max_length=64)
    class_name: str | None = Field(default=None, max_length=100)
    password: str = Field(default="123456", min_length=6, max_length=128)


class TeacherStudentAccountItem(BaseModel):
    user_id: int
    username: str
    full_name: str | None
    student_no: str | None
    class_name: str | None
    role: str
    is_enabled: bool
    created_at: datetime


class TeacherStudentAccountPage(BaseModel):
    items: list[TeacherStudentAccountItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TeacherStudentBatchActionFailedItem(BaseModel):
    user_id: int
    reason: str


class TeacherStudentBatchStatusRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)


class TeacherStudentStatusUpdateResponse(BaseModel):
    user_id: int
    is_enabled: bool
    message: str


class TeacherStudentPasswordResetRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)


class TeacherStudentPasswordResetResponse(BaseModel):
    user_id: int
    must_change_password: bool
    message: str


class TeacherStudentBatchStatusUpdateResponse(BaseModel):
    success_count: int
    failed_count: int
    success_user_ids: list[int]
    failed_items: list[TeacherStudentBatchActionFailedItem]
    message: str


class TeacherStudentBatchPasswordResetRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)
    new_password: str = Field(min_length=6, max_length=128)


class TeacherStudentBatchPasswordResetResponse(BaseModel):
    success_count: int
    failed_count: int
    success_user_ids: list[int]
    failed_items: list[TeacherStudentBatchActionFailedItem]
    message: str
