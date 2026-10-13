from typing import Any

from backend.dependencies import get_add_notebook_entry_use_case, get_get_notebooks_use_case
from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel

from application.notebook.add_notebook_entry import AddNotebookEntryRequest, AddNotebookEntryUseCase
from application.notebook.get_notebooks import GetNotebooksRequest, GetNotebooksUseCase

notebook_router = APIRouter(prefix="/notebooks", tags=["Notebook"])


class AddNotebookEntryPayload(BaseModel):
    title: str
    content: str
    idempotency_key: str | None = None


@notebook_router.get("")
async def list_notebooks(
    document_id: str,
    request_obj: Request, authorization: str | None = Header(None, description="Bearer token"),
    use_case: GetNotebooksUseCase = Depends(get_get_notebooks_use_case),  # noqa: B008
) -> dict[str, Any]:
    token = request_obj.cookies.get("kogniq_session", "") or (authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else (authorization or ""))
    request = GetNotebooksRequest(document_id=document_id, token=token)
    response = await use_case.execute(request)
    return {"notebooks": response.notebooks}


@notebook_router.post("/{document_id}/entries")
async def add_notebook_entry(
    document_id: str,
    payload: AddNotebookEntryPayload,
    request_obj: Request, authorization: str | None = Header(None, description="Bearer token"),
    use_case: AddNotebookEntryUseCase = Depends(get_add_notebook_entry_use_case),  # noqa: B008
) -> dict[str, Any]:
    token = request_obj.cookies.get("kogniq_session", "") or (authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else (authorization or ""))
    request = AddNotebookEntryRequest(
        document_id=document_id,
        token=token,
        title=payload.title,
        content=payload.content,
        idempotency_key=payload.idempotency_key,
    )
    response = await use_case.execute(request)
    return {"status": response.status, "entry_id": response.entry_id}
