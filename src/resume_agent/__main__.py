from resume_agent.config import LLM_MODEL
from resume_agent.llm_connection import smoke_chat

def main():
    print(f"Smoking chat with {LLM_MODEL}")
    print(smoke_chat())

if __name__ == "__main__":
    main()