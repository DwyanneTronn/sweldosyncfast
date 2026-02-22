from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.routers import payroll, employees

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    create_db_and_tables()
    yield
    # Shutdown logic if any (none for now)

app = FastAPI(
    title="SweldoSync Computation Engine",
    description="A modular, API-first payroll engine for the Philippines.",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(payroll.router, prefix="/api/payroll", tags=["Payroll"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])

@app.get("/")
def read_root():
    return {"message": "SweldoSync Engine is Running. Use /docs for API documentation."}
