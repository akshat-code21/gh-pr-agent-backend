from typing import TypedDict, Optional


class AgentState(TypedDict):
    pr_url: str
    github_token: str

    pr_details: dict
    raw_diff: str
    parsed_files: list[dict]
    file_analysis: list[dict]
    review: str
    error: Optional[str]
