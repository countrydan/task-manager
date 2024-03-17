# Task Management API Documentation

Create, update or delete tasks. Filter or sort and get smart suggestions based on existing tasks.

## Table of Contents
1. [Setup Instructions](#setup-instructions)
2. [Endpoints](#endpoints)
3. [Examples](#examples)
4. [Design Decisions](#design-decisions)

## Setup Instructions

To set up the API clone the repo and create a .env file according to the example.

Build an image from the provided docker file:
   ```bash
   docker build -t taskmanager .
   ```
Start a container:
   ```bash
   docker run -d --name taskmanagercont -p 80:80 taskmanager
   ```
and the endpoints should be available at localhost.

Alternatively, install the required Python version (3.11), the dependencies and run the uvicorn command.
   ```bash
   uvicorn src.main:app
   ```

The API will now be running locally on port 8000 by default.

The starting page is the Swagger UI documentation page.

## Endpoints

### Create Task

- **URL:** `/task`
- **Method:** POST
- **Description:** Create a new task.
- **Request Body:**
  ```json
  {
      "title": "Task Title",
      "description": "Task Description",
      "creation_date": "2024-02-15",
      "due_date": "2024-03-20",
      "status": "pending"
  }
  ```
- **Response Body (Success, 201):**
  ```json
  {
      "id": 1,
      "title": "Task Title",
      "description": "Task Description",
      "creation_date": "2024-02-15",
      "due_date": "2024-03-20",
      "status": "pending"
  }
  ```

- **Response Body (Failed, 422):**
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### Create Task with suggestions

- **URL:** `/smart_task`
- **Method:** POST
- **Description:** Create a new task and get suggestions on additional tasks based on the one just created.
- **Request Body:**
  ```json
  {
      "title": "Task Title",
      "description": "Task Description",
      "creation_date": "2024-02-15",
      "due_date": "2024-03-20",
      "status": "pending"
  }
  ```
- **Response Body (Success, 201):**
  ```json
  {
      "id": 1,
      "title": "Task Title",
      "description": "Task Description",
      "creation_date": "2024-02-15",
      "due_date": "2024-03-20",
      "status": "pending",
      "suggestions": ["Suggestions Title", "Another suggestion title"]
  }
  ```

- **Response Body (Failed, 422):**
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### Read Task

- **URL:** `/task`
- **Method:** GET
- **Description:** Get details of a specific task with optional filtering and sorting.
- **Parameters**:
  - sort: Sort by creation or due date, defaults to ascending.
  - desc: Boolean, default is ascending, set this query param to true for descending option.
  - status: Set this to any of the allowed statuses for filtering (pending, in progress, completed).
  - due: To filter by due date set this to a valid date.

### Update Task

- **URL:** `/task`
- **Method:** PUT
- **Description:** Update details of a specific task.
- **Request Body:**
  ```json
  {
      "id": 1,
      "title": "Updated Title",
      "description": "Updated Description",
      "creation_date": "2024-02-15",
      "due_date": "2024-03-25",
      "status": "in progress"
  }
  ```
- **Response Body (Success, 201):**
  ```json
  {
      "id": 1,
      "title": "Updated Title",
      "description": "Updated Description",
      "creation_date": "2024-02-15",
      "due_date": "2024-03-25",
      "status": "in progress"
  }
  ```

- **Response Body (Failed, 422):**
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### Delete Task

- **URL:** `/task`
- **Method:** DELETE
- **Description:** Delete a specific task.
- **Parameters:**
  - id: Task id to delete.

## Examples

### Create Task Example

```bash
curl -X POST http://localhost:8000/task \
     -H 'Content-Type: application/json' \
     -d '{
         "title": "Review pull request",
         "description": "Review Jane Does pr",
         "creation_date": "2024-03-11",
         "due_date": "2024-03-20",
         "status": "in progress"
     }'
```

### Read Task Example

```bash
curl -X GET http://localhost:8000/task
```

## Design Decisions

- **Assumptions:**
  - only one task is created at once
  - creation date set on client side
  - creation date cannot be updated
  - if status is pending than due date can be none
  

