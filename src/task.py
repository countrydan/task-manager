from enum import StrEnum
from datetime import date, datetime
from typing import Any, Annotated


import sqlalchemy
from fastapi import APIRouter, HTTPException, Query

from src.database import database, tasks_table
from src.model import TaskIn, Task, Status, SmartTask
from src.smart_suggestion import get_similar_tasks

router = APIRouter()


class SortBy(StrEnum):
    creation_date = "creation_date"
    due_date = "due_date"


@router.post("/task", response_model=Task, status_code=201)
async def create_task(task: TaskIn):
    data = task.model_dump()
    query = tasks_table.insert().values(data)
    last_task_id = await database.execute(query)
    data.update({"id": last_task_id})
    return data


@router.post("/smart_task", response_model=SmartTask, status_code=201)
async def create_smart_task(task: TaskIn):
    data = task.model_dump()
    existing_tasks = await database.fetch_all(tasks_table.select())
    similar_titles = None
    if existing_tasks:
        existing_tasks = [{**task} for task in existing_tasks]
        similar_tasks = get_similar_tasks(existing_tasks, data)
        similar_titles = [task["title"] for task in similar_tasks]
    query = tasks_table.insert().values(data)
    last_task_id = await database.execute(query)
    data.update({"id": last_task_id})
    return {**data, "suggestions": similar_titles}


@router.get("/task", response_model=list[Task], status_code=200)
async def get_tasks(
    sort: Annotated[
        SortBy | None,
        Query(
            title="Sort",
            description="Sort by creation or due date, defaults to ascending",
        ),
    ] = None,
    desc: Annotated[
        bool,
        Query(
            title="Sort option",
            description="Default is ascending, set this query param to true for descending",
        ),
    ] = False,
    status: Annotated[
        Status | None,
        Query(
            title="Status filter",
            description="Set this to any of the allowed statuses for filtering",
        ),
    ] = None,
    due: Annotated[
        date | None,
        Query(
            title="Due date filter",
            description="To filter by due date set this to a valid date",
        ),
    ] = None,
):
    query = tasks_table.select()
    if status:
        query = query.where(tasks_table.c.status == status.value)
    if due:
        query = query.where(tasks_table.c.due_date == due)
    if sort:
        match sort:
            case SortBy.creation_date:
                order_col = tasks_table.c.creation_date
            case SortBy.due_date:
                order_col = tasks_table.c.due_date
        if desc:
            order_col = sqlalchemy.desc(
                order_col
            )  # this is guarded by the if statement
        query = query.order_by(order_col)  # this too
    return await database.fetch_all(query)


@router.put("/task", response_model=Task)
async def update_task(task: Task):
    old_task = await check_task_exists(task.id)
    if old_task["creation_date"] != task.creation_date:
        raise HTTPException(status_code=409, detail="Cannot update creation date")
    # completed_ts was going to be used for the second criteria in the unique challenge
    completed_ts = None
    if old_task["status"] != task.status and task.status.value == Status.completed:
        completed_ts = datetime.utcnow()
    await database.execute(
        tasks_table.update()
        .where(tasks_table.c.id == task.id)
        .values({**task.model_dump(), "completed_ts": completed_ts})
    )
    updated_task = {
        **await database.fetch_one(
            tasks_table.select().where(tasks_table.c.id == task.id)
        )
    }
    return updated_task


async def check_task_exists(task_id: int) -> dict[str, Any]:
    """Check if task exists in database, if not raise exception, else return record from database as dictionary"""
    task = await database.fetch_one(
        tasks_table.select().where(tasks_table.c.id == task_id)
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/task", status_code=204)
async def delete_task(id: int):
    await check_task_exists(id)
    await database.execute(tasks_table.delete().where(tasks_table.c.id == id))
