from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o", max_tokens=2048, temperature=0.1)