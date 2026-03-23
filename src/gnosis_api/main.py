from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gnosis_api.db import close_db, init_db
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
