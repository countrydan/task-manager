import pytest
from httpx import AsyncClient

tasks = [
    {
        "title": "Another test title",
        "description": "Another test description",
        "creation_date": "2024-02-05",
        "due_date": "2024-05-12",
        "status": "in progress",
    },
    {
        "title": "Test title",
        "description": "Test description",
        "creation_date": "2024-01-01",
        "status": "pending",
    },
    {
        "title": "Third Test title",
        "description": "Third Test description",
        "creation_date": "2023-10-15",
        "due_date": "2023-12-31",
        "status": "completed",
    },
    {
        "title": "Fourth Test title",
        "description": "Fourth Test description",
        "creation_date": "2023-10-10",
        "due_date": "2023-12-01",
        "status": "completed",
    },
]


async def create_task(async_client: AsyncClient, data: dict):
    await async_client.post("/task", json=data)


@pytest.fixture()
async def created_tasks(async_client: AsyncClient):
    [await create_task(async_client, task) for task in tasks]


@pytest.mark.anyio
async def test_create_task(async_client: AsyncClient):
    task = tasks[0]
    response = await async_client.post("/task", json=task)
    assert response.status_code == 201
    assert {"id": 1, **task}.items() <= response.json().items()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "task, msg",
    [
        (
            {
                "title": "Test title",
                "description": "Test description",
                "creation_date": "2024-01-01",
                "status": "completed",
            },
            "Value error, The task is not in pending state, please provide a due date",
        ),
        (
            {
                "title": "Test title",
                "description": "Test description",
                "creation_date": "2024-01-01",
                "due_date": "2023-12-31",
                "status": "in progress",
            },
            "Value error, Due date cannot be less than creation date",
        ),
    ],
)
async def test_create_task_validation_error(async_client: AsyncClient, task, msg):
    response = await async_client.post("/task", json=task)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == msg


@pytest.mark.anyio
async def test_get_tasks(async_client: AsyncClient, created_tasks):
    response = await async_client.get("/task")
    assert response.status_code == 200
    assert len(response.json()) == 4


@pytest.mark.anyio
async def test_get_tasks_sorted(async_client: AsyncClient, created_tasks):
    response = await async_client.get("/task", params={"sort": "creation_date"})
    assert response.status_code == 200
    assert len(response.json()) == 4
    assert [task["id"] for task in response.json()] == [4, 3, 2, 1]


@pytest.mark.anyio
async def test_get_tasks_filtered(async_client: AsyncClient, created_tasks):
    status_response = await async_client.get("/task", params={"status": "completed"})
    due_response = await async_client.get("/task", params={"due": "2024-05-12"})
    due_status_response = await async_client.get(
        "/task", params={"due": "2023-12-01", "status": "completed"}
    )
    assert (
        status_response.status_code,
        due_response.status_code,
        due_status_response.status_code,
    ) == (200, 200, 200)
    assert (
        len(status_response.json()),
        len(due_response.json()),
        len(due_status_response.json()),
    ) == (2, 1, 1)
    assert [task["id"] for task in status_response.json()] == [3, 4]
    assert [task["id"] for task in due_response.json()] == [1]
    assert [task["id"] for task in due_status_response.json()] == [4]


@pytest.mark.anyio
async def test_update_task(async_client: AsyncClient, created_tasks):
    updated_task = {
        "id": 1,
        "title": "Updated test title",
        "description": "Updated test description",
        "creation_date": "2024-02-05",
        "due_date": "2024-05-15",
        "status": "in progress",
    }
    response = await async_client.put("/task", json=updated_task)
    assert updated_task.items() <= response.json().items()


@pytest.mark.anyio
async def test_update_task_not_found(async_client: AsyncClient, created_tasks):
    updated_task = {
        "id": 5,
        "title": "Updated test title",
        "description": "Updated test description",
        "creation_date": "2024-02-05",
        "due_date": "2024-05-15",
        "status": "in progress",
    }
    response = await async_client.put("/task", json=updated_task)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.anyio
async def test_update_task_creation_date(async_client: AsyncClient, created_tasks):
    updated_task = {
        "id": 1,
        "title": "Updated test title",
        "description": "Updated test description",
        "creation_date": "2024-02-06",
        "due_date": "2024-05-15",
        "status": "in progress",
    }
    response = await async_client.put("/task", json=updated_task)
    assert response.status_code == 409
    assert response.json() == {"detail": "Cannot update creation date"}


@pytest.mark.anyio
async def test_delete_task(async_client: AsyncClient, created_tasks):
    task = {
        "title": "To be deleted",
        "description": "this is going to be deleted",
        "creation_date": "2024-02-06",
        "due_date": "2024-05-15",
        "status": "in progress",
    }
    await create_task(async_client, task)
    response = await async_client.delete("/task", params={"id": 5})
    assert response.status_code == 204
    all_tasks = await async_client.get("/task")
    assert 5 not in [task["id"] for task in all_tasks.json()]


@pytest.mark.anyio
async def test_create_smart_suggestion(async_client: AsyncClient, created_tasks):
    task = {
        "title": "Suggest me a test title",
        "description": "Suggestible test description",
        "creation_date": "2023-10-10",
        "due_date": "2023-12-01",
        "status": "pending",
    }
    response = await async_client.post("/smart_task", json=task)
    assert response.status_code == 201
    assert response.json()["suggestions"] is not None
