# GitHub Agent Backend

FastAPI backend for an AI-powered GitHub pull request review agent. The service accepts a pull request URL, fetches PR metadata and the unified diff from GitHub, analyzes the changes with a LangGraph workflow, and posts the generated review back to the pull request as a comment.

## Features

- Fetches pull request metadata and diffs from GitHub.
- Parses unified diffs into per-file hunks with language detection.
- Runs a LangGraph review pipeline for security, correctness, and maintainability feedback.
- Uses OpenRouter through `langchain-openrouter` for LLM calls.
- Publishes the final Markdown review as a GitHub PR comment.

## Tech Stack

- Python 3.12
- FastAPI
- LangGraph
- LangChain OpenRouter
- PyGithub
- unidiff
- uv

## Project Structure

```text
app/
  agent/
    graph.py        # LangGraph workflow definition
    nodes.py        # Review pipeline nodes
    prompts.py      # LLM prompts
    state.py        # Agent state schema
  routers/
    health.py       # Health check route
    review.py       # PR review route
  services/
    diff_parser.py  # Unified diff parser
    github.py       # GitHub API client wrapper
    llm.py          # OpenRouter chat model
  dependencies.py   # FastAPI dependencies
  main.py           # FastAPI app entrypoint
```

## Prerequisites

- Python 3.12
- `uv`
- A GitHub personal access token with access to the target repository and permission to comment on pull requests
- An OpenRouter API key

## Setup

Install dependencies:

```bash
uv sync
```

If the FastAPI and GitHub runtime packages are not already installed in your environment, add them:

```bash
uv add fastapi uvicorn pygithub requests
```

Create a local environment file:

```bash
touch .env
```

Set your OpenRouter API key:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
```

## Running Locally

Start the API server:

```bash
uv run uvicorn app.main:app --reload
```

The service will be available at:

```text
http://127.0.0.1:8000
```

Interactive API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## API

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "OK"
}
```

### Review Pull Request

```http
POST /review
```

Headers:

```http
X-GitHub-Token: <github_personal_access_token>
Content-Type: application/json
```

Body:

```json
{
  "url": "https://github.com/owner/repo/pull/123"
}
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/review \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Token: $GITHUB_TOKEN" \
  -d '{"url":"https://github.com/owner/repo/pull/123"}'
```

Response:

```json
{
  "comment": null,
  "review": "## Overview\n..."
}
```

The service also posts the generated review as an issue comment on the pull request.

## How It Works

1. `/review` receives a pull request URL and a GitHub token.
2. `GithubService` fetches PR metadata and the raw diff.
3. `parse_diff` converts the unified diff into structured file changes.
4. LangGraph runs the review pipeline:
   - fetch PR details
   - fetch diff
   - parse diff
   - analyze files
   - format review
5. The final review is returned in the API response and posted to GitHub.

## Notes

- The GitHub token is passed per request through the `X-GitHub-Token` header.
- The LLM provider is configured in `app/services/llm.py`.
- The current model is `gpt-oss-120b:free` via OpenRouter.
- The agent uses an in-memory LangGraph checkpointer, so state is not persisted across process restarts.
