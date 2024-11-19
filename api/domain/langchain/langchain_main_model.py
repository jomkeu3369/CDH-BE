from dotenv import load_dotenv

from langchain_teddynote import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.domain.note.note_crud import get_note
from api.models import ORM
from api.database import get_db

load_dotenv()
logging.langsmith("deploy_models")
DB_PATH = "src/api/chroma_db"

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

sum_template = """
    다음 항목에 대해서 요약을 진행해 주세요.

    출력은 반드시 한글로 해주세요.

    context : {input}
    output :
"""
# -----------------------------------
#  검색기 설정
# -----------------------------------

persist_db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=OpenAIEmbeddings(),
    collection_name="my_db",
)

VectorStore_retriever = persist_db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k":1, "score_threshold": 0.8}
)

def combine_sources(inputs):
    web_search = inputs["web_search"]
    vector_docs = inputs["vector_docs"]
    return f"Web Search Results:\n{web_search}\n\nVector Store Results:\n{vector_docs}"

def format_docs(docs):
    print(f"문서의 개수 : {len(docs)}")
    return "\n".join([doc.page_content for doc in docs])

async def get_datas(input, db: AsyncSession = Depends(get_db)):
    note_data:ORM.Notes = await get_note(db, input)
    return note_data.content

wrapper = DuckDuckGoSearchAPIWrapper(region="kr-ko", time="w", safesearch="moderate", backend="api", max_results=1)
search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="text")

# -----------------------------------
#  체인 설정
# -----------------------------------

prompt = PromptTemplate.from_template(template)
sum_prompt = PromptTemplate.format_prompt(sum_template)

model = ChatOpenAI(
    model="gpt-3.5-turbo",
    max_tokens=4096,
    temperature=0.7,
)

sum_chain = (
    sum_prompt | model | output_parser
)

chain = (
    {
        "note_data" : get_note,
        "web_search": get_note | sum_chain | search,
        "vector_docs": get_note | sum_chain | VectorStore_retriever | format_docs,
        "note_id": RunnablePassthrough
    }
    | RunnableLambda(lambda x: {"context": combine_sources(x), "note_data": x["note_data"]})
    | prompt
    | model
    | output_parser
)

# 노트 ID
# chain = prompt | model | output_parser


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