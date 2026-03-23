from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gnosis_api.db import close_db, init_db
from gnosis_api.rate_limit import get_ip_limiter
from gnosis_api.routes import (
    dictionary,
    events,
    groups,
    hebrew,
    lexicon,
    meta,
    people,
    places,
    search,
    strongs,
    topics,
    verses,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


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

@app.middleware("http")
async def ip_rate_limit_middleware(request: Request, call_next):
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
app.include_router(lexicon.router)
app.include_router(search.router)
app.include_router(meta.router)


@app.get("/")
async def root():
    return {"message": "Gnosis API", "docs": "/docs"}
