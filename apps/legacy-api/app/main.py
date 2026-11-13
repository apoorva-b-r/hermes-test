from fastapi import FastAPI

from app.routers.accounts import router as accounts_router
from app.routers.debug import router as debug_router


class HeadAsGet:
    """Answer HEAD like GET, without a body.

    FastAPI's GET routes answer HEAD with 405. Doing it here, rather than
    registering a HEAD route next to each GET, keeps one route per endpoint.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "HEAD":
            await self.app(scope, receive, send)
            return

        async def send_without_body(message):
            if message["type"] == "http.response.body":
                message = {**message, "body": b""}
            await send(message)

        await self.app({**scope, "method": "GET"}, receive, send_without_body)


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(HeadAsGet)

app.include_router(accounts_router)
app.include_router(debug_router)
