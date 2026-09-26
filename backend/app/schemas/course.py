from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

CourseStatus = Literal["draft", "published", "archived"]
TaskType = Literal["reading", "assignment", "quiz", "file_upload", "text_response", "external_link", "custom"]
SubmissionStatus = Literal["draft", "submitted"]
ReviewStatus = Literal["pending", "reviewed", "returned", "passed", "failed"]


class CourseBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=120)
    summary: str | None = None
    description: str | None = None
    status: CourseStatus = "draft"
    cover_color: str | None = None
    sort_order: int = 0
    is_active: bool = True


class CourseCreate(CourseBase):
    teacher_ids: list[int] = Field(default_factory=list)
    class_group_ids: list[int] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    summary: str | None = None
    description: str | None = None
    status: CourseStatus | None = None
    cover_color: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None
    teacher_ids: list[int] | None = None
    class_group_ids: list[int] | None = None


class CourseRead(CourseBase):
    id: int
    teacher_count: int = 0
    class_count: int = 0
    module_count: int = 0
    task_count: int = 0
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CoursePage(BaseModel):
    items: list[CourseRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class ClassGroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    grade: str | None = None
    description: str | None = None
    is_active: bool = True


class ClassGroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    grade: str | None = None
    description: str | None = None
    is_active: bool | None = None


class ClassGroupRead(BaseModel):
    id: int
    name: str
    grade: str | None
    description: str | None
    is_active: bool
    member_count: int = 0
    course_count: int = 0
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ClassGroupPage(BaseModel):
    items: list[ClassGroupRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class CourseModuleCreate(BaseModel):
    course_id: int
    title: str = Field(min_length=1, max_length=200)
    summary: str | None = None
    sort_order: int = 0
    is_published: bool = True


class CourseModuleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class CourseModuleRead(BaseModel):
    id: int
    course_id: int
    title: str
    summary: str | None
    sort_order: int
    is_published: bool
    task_count: int = 0
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CourseTaskCreate(BaseModel):
    course_id: int
    module_id: int | None = None
    title: str = Field(min_length=1, max_length=200)
    task_type: TaskType = "assignment"
    summary: str | None = None
    instruction_content: str | None = None
    external_url: str | None = None
    config: dict[str, Any] | None = None
    sort_order: int = 0
    max_score: int | None = None
    is_required: bool = True
    is_published: bool = True
    open_at: datetime | None = None
    due_at: datetime | None = None


class CourseTaskUpdate(BaseModel):
    module_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    task_type: TaskType | None = None
    summary: str | None = None
    instruction_content: str | None = None
    external_url: str | None = None
    config: dict[str, Any] | None = None
    sort_order: int | None = None
    max_score: int | None = None
    is_required: bool | None = None
    is_published: bool | None = None
    open_at: datetime | None = None
    due_at: datetime | None = None


class CourseTaskRead(BaseModel):
    id: int
    course_id: int
    module_id: int | None
    title: str
    task_type: TaskType
    summary: str | None
    instruction_content: str | None
    external_url: str | None
    config: dict[str, Any] | None
    sort_order: int
    max_score: int | None
    is_required: bool
    is_published: bool
    open_at: datetime | None
    due_at: datetime | None
    latest_submission_id: int | None = None
    latest_submission_status: str | None = None
    review_status: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CourseResourceRead(BaseModel):
    id: int
    course_id: int
    module_id: int | None
    title: str
    resource_type: str
    url: str | None
    content: str | None
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TaskSubmissionCreate(BaseModel):
    content: str | None = None
    attachment_url: str | None = None
    status: SubmissionStatus = "submitted"


class TaskSubmissionReviewUpdate(BaseModel):
    review_status: ReviewStatus
    score: int | None = None
    review_comment: str | None = None


class TaskSubmissionRead(BaseModel):
    id: int
    task_id: int
    user_id: int
    content: str | None
    attachment_url: str | None
    status: SubmissionStatus
    score: int | None
    review_status: ReviewStatus
    review_comment: str | None
    reviewed_by: int | None
    reviewed_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TeacherSubmissionItem(TaskSubmissionRead):
    username: str | None = None
    full_name: str | None = None
    student_no: str | None = None
    class_name: str | None = None
    task_title: str | None = None
    course_title: str | None = None
