import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gnosis_api.db import close_db, init_db
from gnosis_api.rate_limit import cleanup_limiters, get_ip_limiter
from gnosis_api.routes import (
    dictionary,
    events,
    greek,
    greek_lexicon,
    groups,
    hebrew,
    keys,
    lexicon,
    meta,
    people,
    places,
    search,
    semantic_search,
    strongs,
    topics,
    verses,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(_periodic_cleanup())
    yield
    task.cancel()
    await close_db()


async def _periodic_cleanup() -> None:
    import time

    from gnosis_api.db import get_keys_db

    while True:
        await asyncio.sleep(300)
        cleanup_limiters()
        try:
            db = get_keys_db()
            cutoff = time.time() - 86400
            await db.execute("DELETE FROM request_log WHERE timestamp < ?", (cutoff,))
            await db.commit()
        except Exception:
            pass


app = FastAPI(
    title="Gnosis API",
    description="Biblical knowledge graph API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_SKIP_RATE_LIMIT = {"/", "/docs", "/redoc", "/openapi.json"}


@app.middleware("http")
async def ip_rate_limit_middleware(request: Request, call_next):
    if request.url.path in _SKIP_RATE_LIMIT:
        return await call_next(request)

    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"

    if not get_ip_limiter().is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests from this IP"},
            headers={"Retry-After": "60"},
        )

    return await call_next(request)


app.include_router(people.router)
app.include_router(places.router)
app.include_router(events.router)
app.include_router(groups.router)
app.include_router(verses.router)
app.include_router(strongs.router)
app.include_router(dictionary.router)
app.include_router(topics.router)
app.include_router(hebrew.router)
app.include_router(greek.router)
app.include_router(lexicon.router)
app.include_router(greek_lexicon.router)
app.include_router(search.router)
app.include_router(semantic_search.router)
app.include_router(meta.router)
app.include_router(keys.router)


@app.get("/")
async def root():
    return {"message": "Gnosis API", "docs": "/docs"}
