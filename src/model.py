from pydantic import BaseModel, Field, model_validator
from datetime import date
from enum import StrEnum


class Status(StrEnum):
    pending = "pending"
    in_progress = "in progress"
    completed = "completed"


class TaskIn(BaseModel):
    title: str = Field(max_items=50)
    description: str = Field(max_length=300)
    creation_date: date
    due_date: date | None = None
    status: Status

    @model_validator(mode="after")
    def check_due_date(self) -> "TaskIn":
        if self.status != Status.pending and self.due_date is None:
            raise ValueError(
                "The task is not in pending state, please provide a due date"
            )
        return self

    @model_validator(mode="after")
    def compare_dates(self) -> "TaskIn":
        if self.due_date and self.due_date < self.creation_date:
            raise ValueError("Due date cannot be less than creation date")
        return self


class Task(TaskIn):
    id: int


class SmartTask(Task):
    suggestions: list[str] | None = None
