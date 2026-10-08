from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DBSession
from app.crud import crud_doc
from app.schemas.doc import DocListItemRead, DocRead

router = APIRouter(prefix="/docs", tags=["docs"])


@router.get("", response_model=list[DocListItemRead])
def list_docs(
    db: DBSession,
    current_user: CurrentUser,
    keyword: str = Query(default=""),
    category: str = Query(default=""),
) -> list[DocListItemRead]:
    docs = crud_doc.list_public_docs(
        db, keyword=keyword, category=category, include_admin_manual=current_user.role == "admin"
    )
    return [DocListItemRead.model_validate(item) for item in docs]


@router.get("/meta/categories", response_model=list[str])
def list_doc_categories(
    db: DBSession,
    current_user: CurrentUser,
) -> list[str]:
    return crud_doc.list_public_categories(db, include_admin_manual=current_user.role == "admin")


@router.get("/{slug}", response_model=DocRead)
def get_doc_by_slug(
    slug: str,
    db: DBSession,
    current_user: CurrentUser,
) -> DocRead:
    doc = crud_doc.get_public_doc_by_slug(db, slug=slug)
    if not doc or (doc.category == "管理员手册" and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    return DocRead.model_validate(doc)
