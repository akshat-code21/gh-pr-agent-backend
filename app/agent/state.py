from typing import NotRequired, Required, TypedDict


class AgentState(TypedDict, total=False):
    pr_url: Required[str]

    pr_details: dict
    raw_diff: str
    parsed_files: list[dict]
    file_analysis: list[dict]
    review: str
    error: NotRequired[str]
