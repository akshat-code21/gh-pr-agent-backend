from langchain_openrouter import ChatOpenRouter


model = ChatOpenRouter(
    model="gpt-oss-120b:free",
    temperature=0,
    max_retries=2,
)