from fastapi import FastAPI
from app.routers.accounts import router as accounts_router
from app.routers.debug import router as debug_router

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.include_router(accounts_router)
app.include_router(debug_router)

