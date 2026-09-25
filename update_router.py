with open("apps/api/src/apps/api/app/routers/learning.py", "r", encoding="utf-8") as f:
    content = f.read()

new_endpoint = """
from pydantic import BaseModel
class AddFlashcardPayload(BaseModel):
    question: str
    answer: str
    difficulty: str
    idempotency_key: str

@learning_router.post("/{document_id}/flashcards")
async def add_flashcard(
    document_id: str,
    payload: AddFlashcardPayload,
    request: Request,
    use_case = Depends(backend.dependencies.get_add_flashcard_use_case)
):
    token = request.cookies.get("kogniq_session", "")
    from application.learning.add_flashcard import AddFlashcardRequest
    req = AddFlashcardRequest(
        document_id=document_id,
        token=token,
        question=payload.question,
        answer=payload.answer,
        difficulty=payload.difficulty,
        idempotency_key=payload.idempotency_key
    )
    
    try:
        response = await use_case.execute(req)
        return response
    except Exception as e:
        if type(e).__name__ == "BackendError":
            from fastapi import HTTPException
            raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e)) from e
        raise
"""
import re

if "@learning_router.post(\"/{document_id}/flashcards\")" not in content:
    # Add imports
    content = content.replace("import backend.dependencies", "import backend.dependencies\nfrom pydantic import BaseModel")
    if "import backend.dependencies" not in content:
         content = "import backend.dependencies\n" + content
    content += new_endpoint

with open("apps/api/src/apps/api/app/routers/learning.py", "w", encoding="utf-8") as f:
    f.write(content)
