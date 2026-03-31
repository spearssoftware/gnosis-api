# Gnosis API

REST API for the Gnosis biblical knowledge graph.

Serves people, places, events, topics, people groups, dictionary entries, cross-references, Hebrew/Greek lexicon data, and verse entities from a curated SQLite database. Includes full-text and semantic search.

## Stack

- Python 3.12, FastAPI, aiosqlite
- sentence-transformers + usearch for semantic search

## Data Source

The read-only content database (`gnosis.db`) is built by [spearssoftware/gnosis](https://github.com/spearssoftware/gnosis) and downloaded from its GitHub releases. The data is licensed under CC-BY-SA 4.0.

## Running Locally

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

Download the database and search index:

```sh
gh release download --repo spearssoftware/gnosis --pattern gnosis.db --dir data
gh release download --repo spearssoftware/gnosis --pattern gnosis.usearch --dir data
```

Install dependencies and start the server:

```sh
uv sync
uv run uvicorn gnosis_api.main:app
```

Server runs at http://localhost:8000. API docs at http://localhost:8000/docs.

## API Keys

All `/v1/*` endpoints require an API key. Create one:

```sh
curl -X POST http://localhost:8000/v1/keys -H "Content-Type: application/json" -d '{"email": "you@example.com"}'
```

Pass the key via the `X-API-Key` header on subsequent requests.

## Tests

```sh
uv run pytest
```

## License

The code in this repository is licensed under the [MIT License](LICENSE).

The data served by this API is licensed under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). See [spearssoftware/gnosis](https://github.com/spearssoftware/gnosis) for details and upstream sources.
