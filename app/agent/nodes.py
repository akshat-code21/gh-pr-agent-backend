import json
from typing import Any

from app.services.github import GithubService
from app.services.diff_parser import parse_diff
from .state import AgentState
from langchain_core.runnables import RunnableConfig
from ..services.llm import model
from langchain_core.messages import SystemMessage, HumanMessage
from .prompts import (
    ANALYZE_FILES_SYSTEM,
    ANALYZE_FILES_USER,
    FORMAT_REVIEW_SYSTEM,
    FORMAT_REVIEW_USER,
)


def fetch_pr_details_node(state: AgentState, config: RunnableConfig):
    configurable = config.get("configurable") or {}
    token = configurable.get("token")
    if not token:
        return {**state, "error": "missing github token"}

    github_client = GithubService(token)
    pr_url = state.get("pr_url")
    pr = github_client.get_repo_pr(pr_url)

    if not pr:
        return {**state, "error": "failed to fetch PR details"}

    pr_details = {
        "title": pr.title,
        "body": pr.body,
        "author": pr.user.login,
        "base_ref": pr.base.ref,
        "head_ref": pr.head.ref,
    }

    state["pr_details"] = pr_details

    return {**state, "pr_details": pr_details}


def fetch_diff_node(state: AgentState, config: RunnableConfig):
    configurable = config.get("configurable") or {}
    token = configurable.get("token")
    if not token:
        return {**state, "error": "missing github token"}

    github_client = GithubService(token)
    pr_url = state.get("pr_url")

    pr_diff = github_client.get_pr_diff(pr_url)

    if not pr_diff:
        return {**state, "error": "failed to fetch PR diff"}

    state["raw_diff"] = pr_diff
    return {**state, "raw_diff": pr_diff}


def parse_diff_node(state: AgentState):
    raw_diff = state.get("raw_diff")
    if not raw_diff:
        return {**state, "error": "missing raw diff"}

    parsed_files = parse_diff(raw_diff)
    state["parsed_files"] = parsed_files
    return {**state, "parsed_files": parsed_files}


def analyze_files_node(state: AgentState):
    messages = [
        SystemMessage(content=ANALYZE_FILES_SYSTEM),
        HumanMessage(
            content=ANALYZE_FILES_USER.format(
                pr_details=json.dumps(state.get("pr_details", {}), ensure_ascii=False),
                parsed_files=json.dumps(
                    state.get("parsed_files", []), ensure_ascii=False
                ),
            )
        ),
    ]
    response = model.invoke(messages)
    file_analysis = _parse_json_list(response.content)
    if file_analysis is None:
        return {**state, "error": "model returned invalid file analysis JSON"}

    state["file_analysis"] = file_analysis
    return {**state, "file_analysis": file_analysis}


def format_review_node(state: AgentState):
    messages = [
        SystemMessage(content=FORMAT_REVIEW_SYSTEM),
        HumanMessage(
            content=FORMAT_REVIEW_USER.format(
                pr_url=state.get("pr_url"),
                pr_details=json.dumps(state.get("pr_details", {}), ensure_ascii=False),
                file_analysis=json.dumps(
                    state.get("file_analysis", []), ensure_ascii=False
                ),
            )
        ),
    ]
    response = model.invoke(messages)
    review = _response_text(response.content)
    if not review:
        return {**state, "error": "model returned empty review"}

    state["review"] = review
    return {**state, "review": review}


def _parse_json_list(content: Any) -> list[dict[str, Any]] | None:
    text = _response_text(content)
    if not text:
        return None

    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        return None
    return value


def _response_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts).strip()
    return ""
