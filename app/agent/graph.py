from app.agent.nodes import analyze_files_node, fetch_diff_node, fetch_pr_details_node, format_review_node, parse_diff_node
from app.agent.state import AgentState
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
import uuid
from langgraph.graph import END

builder = StateGraph(AgentState)

builder.add_node("fetch_pr_details_node",fetch_pr_details_node)
builder.add_node("fetch_diff_node",fetch_diff_node)
builder.add_node("parse_diff_node",parse_diff_node)
builder.add_node("analyze_files_node",analyze_files_node)
builder.add_node("format_review_node",format_review_node)

builder.set_entry_point("fetch_pr_details_node")

def should_continue(state: AgentState) -> str:
    return "error" if state.get("error") else "continue"

builder.add_edge("fetch_pr_details_node","fetch_diff_node")
builder.add_edge("fetch_diff_node","parse_diff_node")
builder.add_edge("parse_diff_node","analyze_files_node")
builder.add_edge("analyze_files_node","format_review_node")

builder.add_conditional_edges(
    "fetch_pr_details_node",
    should_continue,
    {"continue": "fetch_diff_node", "error": END}
)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

def run_agent(pr_url: str, token: str):
    config: RunnableConfig = {"configurable": {"token": token, "thread_id": f"{pr_url}_{uuid.uuid4().hex[:8]}"}}
    state: AgentState = {"pr_url": pr_url}
    result = graph.invoke(state, config=config)
    return result
