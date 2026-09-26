import argparse

import pymysql
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.models import (
    ClassGroup,
    ClassMember,
    Course,
    CourseClass,
    CourseModule,
    CourseResource,
    CourseTask,
    CourseTeacher,
    Doc,
    TaskSubmission,
    User,
)


def init_db() -> None:
    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
    ensure_default_docs()


def ensure_database_exists() -> None:
    settings = get_settings()
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{settings.mysql_db}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def _build_default_docs() -> list[dict]:
    return [
        {
            "title": "平台使用指南",
            "slug": "platform-quick-start",
            "category": "平台指南",
            "sort_order": 10,
            "summary": "学生、教师和管理员的基础使用路径。",
            "content": (
                "# 平台使用指南\n\n"
                "## 学生\n\n"
                "1. 登录后进入“我的课程”。\n"
                "2. 打开课程详情，按模块查看任务和资料。\n"
                "3. 在任务详情页阅读说明并提交文本、附件或外部链接结果。\n\n"
                "## 教师\n\n"
                "1. 在“课程看板”查看自己负责的课程。\n"
                "2. 在“学生管理”导入和维护学生账号。\n"
                "3. 在任务提交列表中查看、评分和反馈。\n\n"
                "## 管理员\n\n"
                "1. 管理用户、教师和管理员账号。\n"
                "2. 配置课程、班级、模块、任务和课程资源。\n"
            ),
            "is_published": True,
        },
        {
            "title": "课程配置说明",
            "slug": "course-config-guide",
            "category": "管理员手册",
            "sort_order": 20,
            "summary": "课程、模块、任务和班级绑定的配置建议。",
            "content": (
                "# 课程配置说明\n\n"
                "- Course 表示一门可发布课程。\n"
                "- ClassGroup 表示自然班或教学班。\n"
                "- CourseModule 用于组织章节、周次或主题单元。\n"
                "- CourseTask 支持 reading、assignment、quiz、file_upload、text_response、external_link、custom。\n"
                "- CourseResource 用于课程资料，可绑定课程或模块。\n\n"
                "建议先创建班级和教师账号，再创建课程并绑定教师、班级，最后配置模块和任务。"
            ),
            "is_published": True,
        },
    ]


def ensure_default_docs() -> None:
    with SessionLocal() as db:
        for item in _build_default_docs():
            existed = db.execute(select(Doc).where(Doc.slug == item["slug"])).scalar_one_or_none()
            if not existed:
                db.add(Doc(**item))
        db.commit()


def _get_or_create_user(
    db,
    *,
    username: str,
    password: str,
    role: str,
    full_name: str,
    student_no: str | None = None,
    class_name: str | None = None,
):
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user:
        return user
    user = User(
        username=username,
        password_hash=get_password_hash(password),
        role=role,
        full_name=full_name,
        student_no=student_no,
        class_name=class_name,
        is_enabled=True,
        must_change_password=False,
    )
    db.add(user)
    db.flush()
    return user


def seed_demo_data() -> None:
    init_db()
    with SessionLocal() as db:
        _get_or_create_user(db, username="admin", password="admin123", role="admin", full_name="系统管理员")
        teacher = _get_or_create_user(db, username="teacher01", password="teacher123", role="teacher", full_name="示例教师")
        students = [
            _get_or_create_user(
                db,
                username="student001",
                password="student123",
                role="student",
                full_name="林同学",
                student_no="S001",
                class_name="通用教学一班",
            ),
            _get_or_create_user(
                db,
                username="student002",
                password="student123",
                role="student",
                full_name="周同学",
                student_no="S002",
                class_name="通用教学一班",
            ),
        ]

        class_group = db.execute(select(ClassGroup).where(ClassGroup.name == "通用教学一班")).scalar_one_or_none()
        if not class_group:
            class_group = ClassGroup(name="通用教学一班", grade="2026", description="通用教学框架演示班级")
            db.add(class_group)
            db.flush()
        for student in students:
            exists = db.execute(
                select(ClassMember.id).where(ClassMember.class_group_id == class_group.id, ClassMember.user_id == student.id)
            ).scalar_one_or_none()
            if not exists:
                db.add(ClassMember(class_group_id=class_group.id, user_id=student.id))

        course = db.execute(select(Course).where(Course.slug == "general-learning-design")).scalar_one_or_none()
        if not course:
            course = Course(
                title="通用学习任务设计",
                slug="general-learning-design",
                summary="演示课程：模块、资料、阅读任务与文本提交。",
                description="一门用于验证通用教学管理框架能力的示例课程，不绑定任何编程语言或特定学科。",
                status="published",
                cover_color="#dbeafe",
                sort_order=10,
                is_active=True,
            )
            db.add(course)
            db.flush()
            db.add(CourseTeacher(course_id=course.id, teacher_id=teacher.id, role_label="主讲教师"))
            db.add(CourseClass(course_id=course.id, class_group_id=class_group.id))
            module = CourseModule(course_id=course.id, title="第一模块：任务理解", summary="理解课程任务、阅读资料并完成一次短文本反馈。", sort_order=10)
            db.add(module)
            db.flush()
            db.add(
                CourseResource(
                    course_id=course.id,
                    module_id=module.id,
                    title="课程说明",
                    resource_type="markdown",
                    content="阅读课程目标、完成方式与评分标准。",
                    sort_order=10,
                )
            )
            task = CourseTask(
                course_id=course.id,
                module_id=module.id,
                title="阅读并提交学习计划",
                task_type="text_response",
                summary="阅读课程说明后，用 100 字左右写下你的学习计划。",
                instruction_content="请说明你准备如何安排本课程学习，以及希望教师在哪些方面提供反馈。",
                max_score=100,
                sort_order=10,
                is_published=True,
            )
            db.add(task)
            db.flush()
            db.add(
                TaskSubmission(
                    task_id=task.id,
                    user_id=students[0].id,
                    content="我会先阅读资料，再按模块完成任务，并在每次反馈后修改学习计划。",
                    status="submitted",
                    version=1,
                )
            )
        db.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-demo", action="store_true", help="创建少量演示账号、课程、班级和任务数据")
    args = parser.parse_args()
    if args.seed_demo:
        seed_demo_data()
    else:
        init_db()
