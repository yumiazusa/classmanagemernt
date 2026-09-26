from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="draft", server_default=text("'draft'"), index=True)
    cover_color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    modules: Mapped[list["CourseModule"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    resources: Mapped[list["CourseResource"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    course_teachers: Mapped[list["CourseTeacher"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    course_classes: Mapped[list["CourseClass"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class ClassGroup(Base):
    __tablename__ = "class_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    grade: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    members: Mapped[list["ClassMember"]] = relationship(back_populates="class_group", cascade="all, delete-orphan")
    course_classes: Mapped[list["CourseClass"]] = relationship(back_populates="class_group", cascade="all, delete-orphan")


class ClassMember(Base):
    __tablename__ = "class_members"
    __table_args__ = (UniqueConstraint("class_group_id", "user_id", name="uq_class_member_group_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    class_group_id: Mapped[int] = mapped_column(ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_class: Mapped[str] = mapped_column(String(24), nullable=False, default="student", server_default=text("'student'"))
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    class_group: Mapped["ClassGroup"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class CourseTeacher(Base):
    __tablename__ = "course_teachers"
    __table_args__ = (UniqueConstraint("course_id", "teacher_id", name="uq_course_teacher"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    course: Mapped["Course"] = relationship(back_populates="course_teachers")
    teacher: Mapped["User"] = relationship()


class CourseClass(Base):
    __tablename__ = "course_classes"
    __table_args__ = (UniqueConstraint("course_id", "class_group_id", name="uq_course_class"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    class_group_id: Mapped[int] = mapped_column(ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    open_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    course: Mapped["Course"] = relationship(back_populates="course_classes")
    class_group: Mapped["ClassGroup"] = relationship(back_populates="course_classes")


class CourseModule(Base):
    __tablename__ = "course_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"), index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    course: Mapped["Course"] = relationship(back_populates="modules")
    tasks: Mapped[list["CourseTask"]] = relationship(back_populates="module", cascade="all, delete-orphan")


class CourseTask(Base):
    __tablename__ = "course_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id: Mapped[int | None] = mapped_column(ForeignKey("course_modules.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    task_type: Mapped[str] = mapped_column(String(32), nullable=False, default="assignment", server_default=text("'assignment'"), index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    instruction_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"), index=True)
    max_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"))
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"), index=True)
    open_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    course: Mapped["Course"] = relationship()
    module: Mapped["CourseModule | None"] = relationship(back_populates="tasks")
    submissions: Mapped[list["TaskSubmission"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class CourseResource(Base):
    __tablename__ = "course_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id: Mapped[int | None] = mapped_column(ForeignKey("course_modules.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False, default="link", server_default=text("'link'"))
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"), index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    course: Mapped["Course"] = relationship(back_populates="resources")


class TaskSubmission(Base):
    __tablename__ = "task_submissions"
    __table_args__ = (UniqueConstraint("task_id", "user_id", "version", name="uq_task_submission_user_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("course_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="submitted", server_default=text("'submitted'"), index=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending", server_default=text("'pending'"), index=True)
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    task: Mapped["CourseTask"] = relationship(back_populates="submissions")
    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="task_submissions")
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by])
