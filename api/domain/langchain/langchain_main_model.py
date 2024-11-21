from dotenv import load_dotenv

from langchain_teddynote import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.domain.note.note_crud import get_note
from api.models import ORM
from api.database import get_db
import re

load_dotenv()
logging.langsmith("deploy_models")
DB_PATH = "./faiss_db"

# --------------------------------------
#  모델 기본 설정
# --------------------------------------

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

temp_template = """
You're an analyst analyzing a project. 
You're given notes data, you have to synthesize it to make an educated guess about how far along the project is and say why.
You're Answer based on context.

notes data:
{note_data}

context:
{context}

FORMAT:
- your answers must be in Korean.
- project progress percentage:
- reason:
- proposals:
- summary:
"""

optimize_template = """
    Convert the following query into a search-optimized form. Extract the keywords and add search operators if necessary.
    Just output the keywords without any additional words.

    query: {query}
"""
# -----------------------------------
#  검색기 설정
# -----------------------------------

loaded_db = FAISS.load_local(
    folder_path=DB_PATH,
    index_name="faiss_index",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True,
)

VectorStore_retriever = loaded_db.as_retriever(
    search_type="similarity",
    search_kwargs={"k":1}
)

def optimize_query(query):
    keywords = re.findall(r'\b\w+\b', query.lower())
    important_words = [word for word in keywords]
    optimized_query = ' '.join([f'{word}' for word in important_words])
    return optimized_query

def combine_sources(inputs):
    web_search = search.invoke(optimize_query(inputs["summarized_query"]))
    vector_docs = format_docs(VectorStore_retriever.invoke(inputs["summarized_query"]))
    return f"Web Search Results:\n{web_search}\n\nVector Store Results:\n{vector_docs}"

def format_docs(docs):
    return "\n".join([doc.page_content for doc in docs])

async def get_datas(note_id, db: AsyncSession = Depends(get_db)):
    note_data:ORM.Notes = await get_note(db, note_id)
    return note_data.content

wrapper = DuckDuckGoSearchAPIWrapper(region="kr-ko", time="w", safesearch="moderate", backend="api", max_results=1)
search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="text")

# -----------------------------------
#  체인 설정
# -----------------------------------

prompt = PromptTemplate.from_template(temp_template)
optimize_prompt = PromptTemplate.from_template(optimize_template)

model = ChatOpenAI(
    model="gpt-4o-mini",
    max_tokens=4096,
    temperature=0.7,
)

optimize_chain = optimize_prompt | model | output_parser

chain = (
    {
        "original_query": RunnablePassthrough(),
        "summarized_query" : optimize_chain 
    } 
    | RunnableLambda(lambda x: {"context": combine_sources(x), "note_data": x["original_query"]})
    | prompt
    | model
    | output_parser
)

# -----------------------------------
#  추가할 사항
# -----------------------------------

'''

    벡터 스토어에 데이터 추가
        메타데이터를 통해서 유저 컬럼 설정
        라우터 추가 필요        

    검색기
        메타데이터를  통해서 유저 컬럼만 검사
        노트 및 기타 데이터들의 최대압축본을 쿼리로 전달

'''