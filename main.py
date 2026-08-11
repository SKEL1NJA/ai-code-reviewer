from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from reviewer import review_code
from schemas import CodeReviewResult

app = FastAPI(title="AI Code Reviewer")

MAX_CODE_LENGTH = 10_000


class ReviewRequest(BaseModel):
    code: str


@app.get("/")
def read_root():
    return {"status": "AI Code Reviewer is running"}


@app.post("/review", response_model=CodeReviewResult)
def review(request: ReviewRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code field cannot be empty")
    if len(request.code) > MAX_CODE_LENGTH:
        raise HTTPException(status_code=400, detail=f"Code exceeds {MAX_CODE_LENGTH} character limit")

    try:
        return review_code(request.code)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {str(e)}")