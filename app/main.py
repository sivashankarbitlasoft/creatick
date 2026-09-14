from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, ensure_database_exists
from app.routers import auth, users, tickets

# Ensure the database exists before creating tables.
ensure_database_exists()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bus Operator App - Ticket System API")

# Allow the Flutter app and Flask UI to call this API from any origin.
# Tighten this to specific origins before going to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add centralized exception handlers so all endpoints return consistent JSON for
# validation, DB integrity, and unexpected errors. Do not change existing
# endpoint behavior for HTTPException which FastAPI already handles.
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
import logging
from sqlalchemy.exc import IntegrityError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Return the validation errors in a predictable structure (422)
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    # Log and return a generic integrity error message (400). Specific handlers
    # at individual endpoints may still raise their own HTTPExceptions.
    logging.exception("Database integrity error")
    return JSONResponse(status_code=400, content={"detail": "Database integrity error"})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Catch-all for unexpected errors — log details server-side but return a
    # generic message to the client to avoid leaking internals.
    logging.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Ticket System API is running"}
