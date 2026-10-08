from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.doc import CourseDoc, Doc


def list_public_docs(db: Session, *, keyword: str = "", category: str = "", include_admin_manual: bool = True) -> list[Doc]:
    statement = select(Doc).where(Doc.is_published.is_(True))
    if not include_admin_manual:
        statement = statement.where(Doc.category != "管理员手册")

    cleaned_keyword = keyword.strip()
    if cleaned_keyword:
        pattern = f"%{cleaned_keyword}%"
        statement = statement.where(
            or_(
                Doc.title.ilike(pattern),
                Doc.summary.ilike(pattern),
                Doc.content.ilike(pattern),
            )
        )

    cleaned_category = category.strip()
    if cleaned_category and cleaned_category != "all":
        statement = statement.where(Doc.category == cleaned_category)

    statement = statement.order_by(Doc.sort_order.asc(), Doc.id.asc())
    return list(db.execute(statement).scalars().all())


def get_public_doc_by_slug(db: Session, *, slug: str) -> Doc | None:
    statement = select(Doc).where(Doc.slug == slug, Doc.is_published.is_(True))
    return db.execute(statement).scalar_one_or_none()


def list_admin_docs(db: Session, *, keyword: str = "", category: str = "") -> list[Doc]:
    statement = select(Doc)

    cleaned_keyword = keyword.strip()
    if cleaned_keyword:
        pattern = f"%{cleaned_keyword}%"
        statement = statement.where(
            or_(
                Doc.title.ilike(pattern),
                Doc.summary.ilike(pattern),
                Doc.content.ilike(pattern),
            )
        )

    cleaned_category = category.strip()
    if cleaned_category and cleaned_category != "all":
        statement = statement.where(Doc.category == cleaned_category)

    statement = statement.order_by(Doc.sort_order.asc(), Doc.id.asc())
    return list(db.execute(statement).scalars().all())


def list_public_categories(db: Session, *, include_admin_manual: bool = True) -> list[str]:
    statement = (
        select(Doc.category)
        .where(Doc.is_published.is_(True), Doc.category.is_not(None), Doc.category != "")
        .group_by(Doc.category)
        .order_by(Doc.category.asc())
    )
    if not include_admin_manual:
        statement = statement.where(Doc.category != "管理员手册")
    return [str(item) for item in db.execute(statement).scalars().all()]


def list_admin_categories(db: Session) -> list[str]:
    statement = (
        select(Doc.category)
        .where(Doc.category.is_not(None), Doc.category != "")
        .group_by(Doc.category)
        .order_by(Doc.category.asc())
    )
    return [str(item) for item in db.execute(statement).scalars().all()]


def get_by_id(db: Session, *, doc_id: int) -> Doc | None:
    return db.get(Doc, doc_id)


def get_by_slug(db: Session, *, slug: str) -> Doc | None:
    statement = select(Doc).where(Doc.slug == slug)
    return db.execute(statement).scalar_one_or_none()


def get_by_slug_excluding_id(db: Session, *, slug: str, exclude_id: int) -> Doc | None:
    statement = select(Doc).where(Doc.slug == slug, Doc.id != exclude_id)
    return db.execute(statement).scalar_one_or_none()


def create_doc(db: Session, *, payload: dict) -> Doc:
    doc = Doc(**payload)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_doc(db: Session, *, doc: Doc, payload: dict) -> Doc:
    for key, value in payload.items():
        setattr(doc, key, value)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def delete_doc(db: Session, *, doc: Doc) -> None:
    db.delete(doc)
    db.commit()


def public_doc_count(db: Session) -> int:
    statement = select(func.count()).select_from(select(Doc.id).where(Doc.is_published.is_(True)).subquery())
    return int(db.execute(statement).scalar_one() or 0)


def list_course_docs(db: Session, *, course_id: int, include_unpublished: bool = False) -> list[CourseDoc]:
    statement = select(CourseDoc).where(CourseDoc.course_id == course_id)
    if not include_unpublished:
        statement = statement.where(CourseDoc.is_published.is_(True))
    statement = statement.order_by(CourseDoc.sort_order.asc(), CourseDoc.id.asc())
    return list(db.execute(statement).scalars().all())


def get_course_doc(db: Session, *, course_id: int, doc_id: int) -> CourseDoc | None:
    return db.execute(select(CourseDoc).where(CourseDoc.course_id == course_id, CourseDoc.id == doc_id)).scalar_one_or_none()


def get_course_doc_by_slug(db: Session, *, course_id: int, slug: str) -> CourseDoc | None:
    return db.execute(select(CourseDoc).where(CourseDoc.course_id == course_id, CourseDoc.slug == slug)).scalar_one_or_none()
