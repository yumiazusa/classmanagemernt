import argparse
import getpass

import pymysql
from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.models import (
    ClassGroup,
    ClassMember,
    Course,
    CourseClass,
    CourseDoc,
    CourseExperience,
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
                "2. 选择已开放的课程并进入对应课程模块。\n\n"
                "## 教师\n\n"
                "1. 在“课程看板”查看自己负责的课程。\n"
                "2. 在“学生管理”导入和维护学生账号。\n"
                "3. 在课程模块中完成授课操作。\n\n"
                "## 管理员\n\n"
                "1. 管理用户、教师和管理员账号。\n"
                "2. 创建课程、连接课程模块、分配教师和班级，并启用课程。\n"
            ),
            "is_published": True,
        },
        {
            "title": "课程配置说明",
            "slug": "course-config-guide",
            "category": "管理员手册",
            "sort_order": 20,
            "summary": "课程模块与授课范围的配置说明。",
            "content": (
                "# 课程配置说明\n\n"
                "- Course 保存课程名称和启停状态。\n"
                "- ClassGroup 表示自然班或教学班。\n"
                "- CourseExperience 连接已接入的课程模块。\n\n"
                "建议先创建教师和班级，再创建课程并分配授课范围。连接课程模块后方可启用课程。"
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
        must_change_password=True,
    )
    db.add(user)
    db.flush()
    return user


def _clear_demo_data(db) -> None:
    if get_settings().app_env == "production":
        raise SystemExit("生产环境禁止重置演示数据。")
    admin = db.execute(select(User).where(User.username == "admin", User.role == "admin")).scalar_one_or_none()
    if admin is None:
        raise SystemExit("未找到现有 admin 管理员，已取消重置。")
    for model in (
        TaskSubmission, CourseResource, CourseTask, CourseModule, CourseDoc,
        CourseExperience, CourseTeacher, CourseClass, ClassMember, Course,
        ClassGroup, Doc,
    ):
        db.execute(delete(model))
    db.execute(delete(User).where(User.id != admin.id))
    db.flush()
    for item in _build_default_docs():
        db.add(Doc(**item))


def seed_demo_data(*, reset_existing: bool = False) -> None:
    init_db()
    with SessionLocal() as db:
        if reset_existing:
            _clear_demo_data(db)
        else:
            _get_or_create_user(db, username="admin", password="admin123", role="admin", full_name="系统管理员")

        teachers = {}
        for username, name in (("teacher_wang", "王宁"), ("teacher_chen", "陈思")):
            teachers[username] = _get_or_create_user(
                db, username=username, password="Teacher@2026", role="teacher", full_name=name,
            )

        class_specs = (
            ("2026级数字经济1班", "数字经济", (("202601001", "林悦"), ("202601002", "周明远"), ("202601003", "李可欣"), ("202601004", "赵一诺"))),
            ("2026级工商管理2班", "工商管理", (("202602001", "陈雨桐"), ("202602002", "刘思源"), ("202602003", "黄子涵"), ("202602004", "吴佳怡"))),
        )
        classes = {}
        for class_name, major, students in class_specs:
            class_group = db.execute(select(ClassGroup).where(ClassGroup.name == class_name)).scalar_one_or_none()
            if class_group is None:
                class_group = ClassGroup(name=class_name, grade="2026", description=f"2026 级{major}专业教学班")
                db.add(class_group)
                db.flush()
            classes[class_name] = class_group
            for student_no, full_name in students:
                student = _get_or_create_user(
                    db, username=student_no, password="Student@2026", role="student",
                    full_name=full_name, student_no=student_no, class_name=class_name,
                )
                exists = db.execute(select(ClassMember.id).where(
                    ClassMember.class_group_id == class_group.id, ClassMember.user_id == student.id,
                )).first()
                if not exists:
                    db.add(ClassMember(class_group_id=class_group.id, user_id=student.id))

        course_specs = (
            (
                "lets-digital-economy-demo", "数字经济案例与分析（示例）", "teacher_wang", "2026级数字经济1班",
                "从平台企业与产业数字化案例出发，练习问题分析与证据表达。",
                "案例分析入门", "case-study-guide",
                "# 案例分析入门\n\n本课程示例围绕数字经济案例开展讨论。\n\n"
                "## 学习目标\n\n1. 识别案例中的参与方与关键问题。\n2. 用公开证据支持判断。\n3. 在课堂讨论后修订结论。\n\n"
                "课程模块尚未接入，当前文档供管理员预览。",
            ),
            (
                "lets-platform-economics-demo", "平台经济学（示例）", "teacher_chen", "2026级工商管理2班",
                "以双边市场和网络效应为线索，练习平台商业模式分析。",
                "平台经济学学习指引", "platform-economics-guide",
                "# 平台经济学学习指引\n\n本课程示例介绍平台市场的基础观察方法。\n\n"
                "## 学习目标\n\n1. 区分平台两侧用户及价值交换。\n2. 观察网络效应与定价策略。\n3. 结合案例讨论治理问题。\n\n"
                "课程模块尚未接入，当前文档供管理员预览。",
            ),
        )
        for order, (slug, title, teacher_key, class_name, summary, doc_title, doc_slug, content) in enumerate(course_specs, 1):
            course = db.execute(select(Course).where(Course.slug == slug)).scalar_one_or_none()
            if course is None:
                course = Course(
                    title=title, slug=slug, summary=summary, description="示例课程；连接正式课程模块后方可启用。",
                    status="draft", is_active=False, sort_order=order * 10,
                )
                db.add(course)
                db.flush()
            if db.get(CourseExperience, course.id) is None:
                db.add(CourseExperience(course_id=course.id, experience_key="unlinked"))
            teacher = teachers[teacher_key]
            class_group = classes[class_name]
            if not db.execute(select(CourseTeacher.id).where(CourseTeacher.course_id == course.id, CourseTeacher.teacher_id == teacher.id)).first():
                db.add(CourseTeacher(course_id=course.id, teacher_id=teacher.id, role_label="主讲教师"))
            if not db.execute(select(CourseClass.id).where(CourseClass.course_id == course.id, CourseClass.class_group_id == class_group.id)).first():
                db.add(CourseClass(course_id=course.id, class_group_id=class_group.id))
            if not db.execute(select(CourseDoc.id).where(CourseDoc.course_id == course.id, CourseDoc.slug == doc_slug)).first():
                db.add(CourseDoc(
                    course_id=course.id, title=doc_title, slug=doc_slug, summary=summary,
                    content=content, sort_order=10, is_published=True,
                ))
        db.commit()


def bootstrap_admin() -> None:
    init_db()
    with SessionLocal() as db:
        existing = db.execute(select(User).where(User.username == "admin")).scalar_one_or_none()
        if existing:
            print("管理员 admin 已存在，未修改现有账号或密码。")
            return
        password = getpass.getpass("设置管理员 admin 的初始密码（至少 12 位）：")
        if len(password) < 12:
            raise SystemExit("初始密码至少需要 12 位。")
        confirmation = getpass.getpass("再次输入初始密码：")
        if password != confirmation:
            raise SystemExit("两次输入的密码不一致。")
        _get_or_create_user(db, username="admin", password=password, role="admin", full_name="系统管理员")
        db.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--seed-demo", action="store_true", help="幂等创建演示账号、班级、未连接课程及课程文档")
    modes.add_argument("--reset-demo", action="store_true", help="仅保留现有 admin 并重建本地演示数据")
    modes.add_argument("--bootstrap-admin", action="store_true", help="交互创建生产初始管理员，不写入固定密码")
    args = parser.parse_args()
    if args.seed_demo:
        seed_demo_data()
    elif args.reset_demo:
        seed_demo_data(reset_existing=True)
    elif args.bootstrap_admin:
        bootstrap_admin()
    else:
        init_db()
