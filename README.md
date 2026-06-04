# FastAPI URL Shortener

A compact **URL shortener** REST API: **FastAPI + SQLite**, base62 short codes,
redirects, and per-link hit stats. Typed models, auto Swagger docs, tested.

> Portfolio sample by **Vladimir Podlevskikh** — Python developer & automation engineer.
> Small web apps & API backends (FastAPI / Flask / Django) are a service I offer.

## Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/shorten` | `{"url": "..."}` → short code |
| GET  | `/{code}` | 307 redirect to the target |
| GET  | `/stats/{code}` | hit count for a code |

## Run
```bash
pip install -r requirements.txt
uvicorn app:app --reload
# http://127.0.0.1:8000/docs
pytest -q
```

## License
MIT
