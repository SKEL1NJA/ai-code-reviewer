from pydantic import BaseModel, Field
from typing import List


class Issue(BaseModel):
    severity: str = Field(description="One of: low, medium, high, critical")
    description: str = Field(description="What the issue is")
    line_reference: str = Field(description="Line number or code snippet where this occurs, if identifiable")
    suggestion: str = Field(description="Concrete fix or improvement")


class CategoryReview(BaseModel):
    score: int = Field(description="Score from 0 (very poor) to 10 (excellent)")
    summary: str = Field(description="1-2 sentence overview of this category")
    issues: List[Issue] = Field(description="Specific issues found, empty list if none")


class CodeReviewResult(BaseModel):
    security: CategoryReview
    performance: CategoryReview
    readability: CategoryReview
    overall_summary: str = Field(description="2-3 sentence overall verdict")