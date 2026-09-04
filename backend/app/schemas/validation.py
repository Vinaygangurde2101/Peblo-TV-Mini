from pydantic import BaseModel
from typing import List, Optional


class ShowValidationReport(BaseModel):
    show_id: str
    show_title: str
    problems: List[str]


class ValidationReportResponse(BaseModel):
    is_publishable: bool
    total_blockers: int
    shows_count: int
    episodes_count: int
    shows_with_issues: List[ShowValidationReport] = []
