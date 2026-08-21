from langchain_ollama import ChatOllama
from resume_agent.config import LLM_MODEL

def get_llm() -> ChatOllama:
    return ChatOllama(
        model=LLM_MODEL,
        temprature=0,
    )

