from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults

load_dotenv()

output_parser = StrOutputParser()

template = """
You're an analyst analyzing a project. 
You're given notes data, ERD data, and API statement data, and you have to synthesize it to make an educated guess about how far along the project is and say why.

notes data:
{note_data}

ERD data:
{erd_data}

API statement data:
{api_data}

FORMAT:
- your answers must be in Korean.
- project progress percentage:
- reason:
- proposals:
- summary:
"""

wrapper = DuckDuckGoSearchAPIWrapper(region="kr-ko", time="w", safesearch="moderate", backend="api", max_results=1)
search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="text")

prompt = PromptTemplate.from_template(template)

model = ChatOpenAI(
    model="gpt-4o",
    max_tokens=4096,
    temperature=0.7,
)

# chain = (
#     {
#         "web_search": search,
#         "vector_docs": VectorStore_retriever | format_docs,
#         "erd_data": search,
#         "api_data": VectorStore_retriever | format_docs,
#         "note_data": note,
#     }
#     | RunnableLambda(lambda x: {"context": combine_sources(x), "question": x["question"]})
#     | prompt
#     | model
#     | output_parser
# )

chain = prompt | model | output_parser