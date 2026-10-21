from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Status = Literal["TODO", "IN_PROGRESS", "DONE"]
Priority = Literal["LOW", "MEDIUM", "HIGH"]

class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10000)
    priority: Priority = "MEDIUM"
    status: Status = "TODO"
    assignee: str = Field(default="Unassigned", min_length=1, max_length=120)

class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def reject_nulls(cls, values):
        if isinstance(values, dict) and any(v is None for v in values.values()):
            raise ValueError("Task fields cannot be null")
        return values

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    priority: Priority | None = None
    status: Status | None = None
    assignee: str | None = Field(default=None, min_length=1, max_length=120)

class TaskOut(TaskCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StatsOut(BaseModel):
    total: int
    todo: int
    inProgress: int
    done: int
