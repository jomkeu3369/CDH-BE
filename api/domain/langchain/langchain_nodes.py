from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from typing import Dict, Any
from api.domain.langchain.langchain_DB import db
from api.domain.langchain.langchain_schema import MainState


# ----------------------------
# 검색 노드
# ----------------------------

async def vectorDB_retriever(state: MainState):
    ''' LLM에게 전달할 사전 정보를 FAISS Vector Store에서 검색합니다. '''

    print("----- VECTORDB RETRIEVE -----")
    query = state["optimize_query"]
    user_id = state["user_id"]
    note_id = state["note_id"]

    VectorStore_retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={
            "k": 4,
            "filter": {"user_id": user_id, "note_id": note_id}
        },
    )
    
    documents = await VectorStore_retriever.ainvoke(query)
    return {"vector_store_context": documents, "optimize_query": query}

async def web_retriever(state: MainState):
    ''' 웹 검색 후 관련 정보를 가져옵니다. '''

    print("-----  WEB SEARCH ----- ")
    question = state["optimize_query"]
    documents = state["web_search_context"]

    wrapper = DuckDuckGoSearchAPIWrapper(region="kr-ko", time="y", safesearch="moderate", backend="api", max_results=4)
    search = DuckDuckGoSearchResults(api_wrapper=wrapper, output_format="list")

    docs = await search.ainvoke({"query": question})
    web_results = "\n".join([d["snippet"] for d in docs])
    web_results = Document(page_content=web_results)
    documents.append(web_results)

    return {"web_search_context": documents}

# ----------------------------
# 쿼리 재작성 노드
# ----------------------------

async def rewrite_query_without_counter(state: MainState):
    ''' original_query를 검색을 수월하게 할 수 있도록 최적화 합니다. '''

    print("----- REWRITE WITHOUT COUNTER -----")
    query = state["original_query"]

    template = """
        Here's your documentation information
        We want to search for information that will help us with the user's documentation information provided. Please write a search sentence that will yield good results.

        Don't make any other additional comments.
        Do not use special characters such as “”. 

        Answers must be printed in English.
        ------------------------------------------

        query: {query}
    """
    

    model = ChatOpenAI(model="gpt-4o-mini", max_tokens=4096, temperature=0.6)
    chain = PromptTemplate.from_template(template) | model | StrOutputParser()
    generation = await chain.ainvoke(input={"query": query})
    return {"optimize_query": generation}

async def rewrite_query_with_counter(state: MainState):
    '''
        original_query를 바탕으로 optimize_query를 재작성 합니다. (카운터 증가)
    '''

    print("----- REWRITE WITH COUNTER -----")
    query = state["original_query"]
    counter = state["counter"]

    template = """
        Here's your documentation information
        We want to search for information that will help us with the user's documentation information provided. Please write a search sentence that will yield good results.

        Don't make any other additional comments.
        Do not use special characters such as “”. 

        Answers must be printed in English.
        ------------------------------------------

        query: {query}
    """
    

    model = ChatOpenAI(model="gpt-4o-mini", max_tokens=4096, temperature=0.6)
    chain = PromptTemplate.from_template(template) | model | StrOutputParser()
    generation = await chain.ainvoke(input={"query": query})
    return {"optimize_query": generation, "counter": counter + 1}

# ----------------------------
# 문서 및 답변 평가 노드
# ----------------------------

async def grade_vectorDB_documents(state: MainState) -> Dict[str, Any]:
    '''
        가져온 문서가 사용자 쿼리와 일치한지 유사도를 검사합니다.
    '''
    print("----- GRADDE VECTORDB -----")
    query = state["original_query"]
    documents = state["vector_store_context"]
    
    filtered_docs = []

    template = """
        These are the user's document information (query) and the information obtained through web search (context).

        If you think the context is relevant to the query, print “Yes”; if not, print “No”.
        -----------------------------------------------------
        query: {note_data}

        -----------------------------------------------------
        context: {context}
    """
    model = ChatOpenAI(model="gpt-4o-mini", max_tokens=4096, temperature=0)
    chain = PromptTemplate.from_template(template) | model | StrOutputParser()

    for doc in documents:
        grade = await chain.ainvoke(input={"note_data": query, "context": doc.page_content})
        if grade.lower() == "yes":
            print("---GRADE: vectorDB DOCUMENT RELEVANT---")
            filtered_docs.append(doc)
        else:
            print("---GRADE: vectorDB DOCUMENT NOT RELEVANT---")

    return {"vector_store_context": filtered_docs, "original_query": query}

async def grade_web_documents(state: MainState) -> Dict[str, Any]:
    print("----- GRADDE WEB -----")
    query = state["original_query"]
    documents = state["web_search_context"]
    
    filtered_docs = []

    template = """
        These are the user's document information (query) and the information obtained through web search (context).

        If you think the context is relevant to the query, print “Yes”; if not, print “No”.
        -----------------------------------------------------
        query: {note_data}

        -----------------------------------------------------
        context: {context}
    """
    model = ChatOpenAI(model="gpt-4o-mini", max_tokens=4096, temperature=0)
    chain = PromptTemplate.from_template(template) | model | StrOutputParser()

    for doc in documents:
        grade = await chain.ainvoke(input={"note_data": query, "context": doc.page_content})
        if grade.lower() == "yes":
            print("---GRADE: WEB DOCUMENT RELEVANT---")
            filtered_docs.append(doc)
        else:
            print("---GRADE: WEB DOCUMENT NOT RELEVANT---")

    return {"web_search_context": filtered_docs, "original_query": query}

async def grade_generation(state: MainState):
    print("----- GRADDE GENERATION -----")
    query = state["original_query"]
    generation = state["generation"]
    
    template = """
        Return “Yes” if you think the answer LLM generated for your document information (query) is a useful answer, or “No” if you don't.
        -----------------------------------------------------
        query: {note_data}

        -----------------------------------------------------
        answer: {answer}
    """
    model = ChatOpenAI(model="gpt-4o-mini", max_tokens=4096, temperature=0)
    chain = PromptTemplate.from_template(template) | model | StrOutputParser()
    result = await chain.ainvoke(input={
        "note_data":query, "answer": generation
    })

    state["self_rag"] = True if result.lower() == "yes" else False
    counter = state["counter"] if state["self_rag"] else 0
    
    return {"self_rag":state["self_rag"], "self_rag_counter":state["self_rag_counter"] + 1, "counter": counter}

# ----------------------------
# 최종 답변 생성 노드
# ----------------------------

async def generation(state: MainState):
    print("----- GENERATION -----")
    note_data = state["original_query"]
    erd_data = state["erd_query"]
    api_data = state["api_query"]
    generation = state["generation"]
    vector_store_context = state["vector_store_context"]
    web_search_context = state["web_search_context"]

    template = """
        You're an analyst analyzing a project. 
        You're given notes data, ERD data, and API statement data, and you have to synthesize it to make an educated guess about how far along the project is and say why.
        You're Answer based on context.
        
        notes data:
        {note_data}

        ERD data:
        {erd_data}

        API statement data:
        {api_data}

        context:
            web_serach: {web_search}

            vectorDB: {vectorDB}

        FORMAT:
        - your answers must be in Korean.
        - project progress percentage:
        - reason:
        - proposals:
        - summary:
        """
    
    model = ChatOpenAI(model="gpt-4o-mini", max_tokens=4096, temperature=0.4)
    chain = PromptTemplate.from_template(template) | model | StrOutputParser()
    generation = await chain.ainvoke({"note_data": note_data, "erd_data": erd_data, "api_data": api_data, "web_search": web_search_context, "vectorDB": vector_store_context})
    return {"generation": generation}
