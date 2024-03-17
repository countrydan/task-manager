from tests.test_task import tasks
from src.smart_suggestion import get_similar_tasks


def test_get_similar_tasks():
    new_task = {
        "title": "Updated test title",
        "description": "Updated test description",
        "creation_date": "2024-02-06",
        "due_date": "2024-05-15",
        "status": "in progress",
    }
    similar_tasks = get_similar_tasks(tasks, new_task)
    assert similar_tasks is not None
