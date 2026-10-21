from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest
from fastapi import Response, Request
from time import perf_counter

from .config import settings
from .db import get_db
from .models import Task
from .schemas import StatsOut, TaskCreate, TaskOut, TaskUpdate

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
REQUESTS = Counter("http_requests_total", "Completed HTTP requests", ["method", "handler", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP response latency", ["handler"])

@app.middleware("http")
async def observe_requests(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    handler = getattr(route, "path", "unmatched")
    if request.url.path != "/metrics":
        REQUESTS.labels(request.method, handler, str(response.status_code)).inc()
        LATENCY.labels(handler).observe(perf_counter() - start)
    return response

@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.exception_handler(SQLAlchemyError)
def database_failure(request, exc):
    # Never return driver errors: they may contain connection details.
    return JSONResponse(status_code=503, content={"detail": "Database temporarily unavailable"})

@app.get("/")
def root():
    return {"service": settings.app_name, "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(select(func.count(Task.id)))
    return {"status": "READY"}

@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return list(db.scalars(select(Task).order_by(Task.id.desc())))

@app.get("/api/tasks/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    rows = db.execute(select(Task.status, func.count(Task.id)).group_by(Task.status)).all()
    counts = {status: count for status, count in rows}
    return StatsOut(total=sum(counts.values()), todo=counts.get("TODO", 0), inProgress=counts.get("IN_PROGRESS", 0), done=counts.get("DONE", 0))

@app.get("/api/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.put("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
