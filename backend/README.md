# RepoIcon Backend

FastAPI backend service for the RepoIcon project.

## Setup

1. Install PDM if you haven't already:
```bash
curl -sSL https://pdm-project.org/install-pdm.py | python3 -
```

2. Install dependencies:
```bash
pdm install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

## Development

Start the development server:
```bash
pdm run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access:
- API docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json 