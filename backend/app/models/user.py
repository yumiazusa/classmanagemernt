from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"), index=True)
    must_change_password: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
        index=True,
    )
    student_no: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    class_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    task_submissions: Mapped[list["TaskSubmission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="TaskSubmission.user_id",
    )
