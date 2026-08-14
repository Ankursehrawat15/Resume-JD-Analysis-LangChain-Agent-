from langchain_ollama import ChatOllama
from resume_agent.config import LLM_MODEL

def smoke_chat():
    llm = ChatOllama(
        model=LLM_MODEL,
        temperature=0.0,
    )
    
    response = llm.invoke("Reply with exactly: Hi I am llama model")
    return response.content

