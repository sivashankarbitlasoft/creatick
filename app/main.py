from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, ensure_database_exists
from app.routers import auth, users, tickets


from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
import logging
from sqlalchemy.exc import IntegrityError

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

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = ".".join(str(x) for x in first["loc"] if x != "body")
    return JSONResponse(status_code=422, content={
        "code": 422,
        "message": f"{field}: {first['msg']}"
    })

@app.exception_handler(IntegrityError)
async def integrity_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={
        "code": 409,
        "message": "A ticket with this sub-domain and app type already exists."
    })

@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={
        "code": 500,
        "message": "Something went wrong while processing your request."
    })