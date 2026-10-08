from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlatformDocCategory = Literal["平台指南", "管理员手册"]


class DocListItemRead(BaseModel):
    id: int
    title: str
    slug: str
    summary: str | None
    category: str
    sort_order: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DocRead(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    summary: str | None
    category: str
    sort_order: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AdminDocItemRead(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    summary: str | None
    category: str
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AdminDocCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    summary: str | None = None
    category: PlatformDocCategory = "平台指南"
    sort_order: int = 0
    is_published: bool = True


class AdminDocUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    category: PlatformDocCategory | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class AdminDocDeleteResponse(BaseModel):
    id: int
    message: str


class CourseDocCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    summary: str | None = None
    sort_order: int = 0
    is_published: bool = True


class CourseDocUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    sort_order: int | None = None
    is_published: bool | None = None


class CourseDocRead(BaseModel):
    id: int
    course_id: int
    title: str
    slug: str
    content: str
    summary: str | None
    sort_order: int
    is_published: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
