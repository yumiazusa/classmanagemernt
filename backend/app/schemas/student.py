from datetime import datetime

from pydantic import BaseModel

from app.schemas.course import ReviewStatus, SubmissionStatus, TaskType
from app.schemas.user import RoleType


class StudentDashboardProfile(BaseModel):
    id: int
    username: str
    full_name: str | None
    student_no: str | None
    class_name: str | None
    role: RoleType


class StudentDashboardSummary(BaseModel):
    total_courses: int
    total_tasks: int
    submitted_count: int
    reviewed_count: int
    returned_count: int
    pending_count: int
    not_started_count: int


class StudentDashboardRecentItem(BaseModel):
    task_id: int
    course_id: int
    title: str
    course_title: str
    task_type: TaskType
    latest_status: SubmissionStatus
    review_status: ReviewStatus
    latest_updated_at: datetime


class StudentDashboardRead(BaseModel):
    profile: StudentDashboardProfile
    summary: StudentDashboardSummary
    recent_items: list[StudentDashboardRecentItem]
