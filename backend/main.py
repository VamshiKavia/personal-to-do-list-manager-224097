import os
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

# In-memory store for todos. In a production system this would be a database.
_TODOS: Dict[int, Dict] = {}
_NEXT_ID = 1


class TodoCreate(BaseModel):
    """Pydantic model for creating a todo item."""
    title: str = Field(..., description="Short title for the todo item", min_length=1, max_length=200)
    completed: bool = Field(False, description="Completion status of the todo item")

    @validator("title")
    def validate_title(cls, v: str) -> str:
        # Basic sanitization/validation to avoid empty/whitespace only
        if not v or not v.strip():
            raise ValueError("Title must not be empty")
        return v.strip()


class TodoUpdate(BaseModel):
    """Pydantic model for updating a todo item."""
    title: Optional[str] = Field(None, description="Updated title for the todo item", min_length=1, max_length=200)
    completed: Optional[bool] = Field(None, description="Updated completion status")

    @validator("title")
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty")
        return v


class Todo(BaseModel):
    """Pydantic model representing a full todo item."""
    id: int = Field(..., description="Unique identifier of the todo item")
    title: str = Field(..., description="Short title for the todo item")
    completed: bool = Field(False, description="Completion status of the todo item")


def _get_allowed_origins() -> List[str]:
    """
    Determine allowed CORS origins based on environment variables.
    We allow REACT_APP_FRONTEND_URL when set, otherwise default to http://localhost:3000.
    Multiple origins can be provided as a comma-separated list.
    """
    raw = os.getenv("REACT_APP_FRONTEND_URL", "http://localhost:3000")
    # Support comma-separated origins
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """Create and configure the FastAPI app with CORS and routes."""
    app = FastAPI(
        title="Todo List API",
        description="A simple FastAPI backend providing CRUD operations for a Todo list. "
                    "Use the /api/todos endpoints to manage items.",
        version="1.0.0",
        openapi_tags=[
            {"name": "health", "description": "Health and metadata endpoints"},
            {"name": "todos", "description": "CRUD operations for todo items"},
        ],
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["health"], summary="Health Check", description="Simple health check endpoint.")
    def health_check():
        """Health check endpoint returning a simple status payload."""
        return {"status": "ok"}

    # PUBLIC_INTERFACE
    @app.get("/api/todos", response_model=List[Todo], tags=["todos"], summary="List Todos",
             description="Retrieve all todo items.")
    def list_todos() -> List[Todo]:
        """Return all todos as a list."""
        return [Todo(**item) for item in _TODOS.values()]

    # PUBLIC_INTERFACE
    @app.post("/api/todos", response_model=Todo, status_code=status.HTTP_201_CREATED,
              tags=["todos"], summary="Create Todo",
              description="Create a new todo item with title and optional completed flag.")
    def create_todo(payload: TodoCreate) -> Todo:
        """Create a new todo and return it."""
        global _NEXT_ID
        todo_id = _NEXT_ID
        _NEXT_ID += 1
        data = {"id": todo_id, "title": payload.title, "completed": payload.completed}
        _TODOS[todo_id] = data
        return Todo(**data)

    # PUBLIC_INTERFACE
    @app.put("/api/todos/{todo_id}", response_model=Todo, tags=["todos"], summary="Update Todo",
             description="Update the fields of a todo item by ID.")
    def update_todo(todo_id: int, payload: TodoUpdate) -> Todo:
        """Update a todo item by ID."""
        if todo_id not in _TODOS:
            raise HTTPException(status_code=404, detail="Todo not found")
        current = _TODOS[todo_id]
        if payload.title is not None:
            current["title"] = payload.title
        if payload.completed is not None:
            current["completed"] = payload.completed
        _TODOS[todo_id] = current
        return Todo(**current)

    # PUBLIC_INTERFACE
    @app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT,
                tags=["todos"], summary="Delete Todo", description="Delete a todo item by ID.")
    def delete_todo(todo_id: int):
        """Delete a todo by ID."""
        if todo_id not in _TODOS:
            raise HTTPException(status_code=404, detail="Todo not found")
        del _TODOS[todo_id]
        return None

    return app


app = create_app()
