import os
from dotenv import load_dotenv

from langchain_teddynote import logging

from langgraph.graph import StateGraph, START, END
from langchain_teddynote.graphs import visualize_graph

from api.domain.langchain.langchain_schema import MainState
from api.domain.langchain.langchain_nodes import *


load_dotenv()
logging.langsmith("deploy_models")
DB_PATH = os.getenv("DB_path")

def decide_to_vectorDB(state: MainState):
    if len(state["vector_store_context"]) > 0:
        return "STOP"
    else:
        return "SEARCH"

def decide_to_websearch(state: MainState):
    if state["counter"] >= 6 or len(state["web_search_context"]) > 0:
        return "STOP"
    else:
        return "RESEARCH" 
    
def decide_to_generate(state: MainState):
    if state["self_rag_counter"] > 1 or state["self_rag"]:
        return "HALT"
    else:
        return "RETRY" 

# 그래프 엣지 추가

workflow = StateGraph(MainState)

workflow.add_node("vectorDB_retriever", vectorDB_retriever)
workflow.add_node("rewrite_query_without_counter", rewrite_query_without_counter)
workflow.add_node("rewrite_query_with_counter", rewrite_query_with_counter)
workflow.add_node("grade_vectorDB_documents", grade_vectorDB_documents)
workflow.add_node("grade_web_documents", grade_web_documents)
workflow.add_node("web_retriever", web_retriever)
workflow.add_node("generate", generation)
workflow.add_node("grade_generation", grade_generation)

workflow.add_edge(START, "rewrite_query_without_counter")
workflow.add_edge("rewrite_query_without_counter", "vectorDB_retriever")
workflow.add_edge("vectorDB_retriever", "grade_vectorDB_documents")

workflow.add_conditional_edges(
    "grade_vectorDB_documents", # 출발지
    decide_to_vectorDB,
    {
        "STOP": "generate",
        "SEARCH": "rewrite_query_with_counter",
    },
)

workflow.add_edge("rewrite_query_with_counter", "web_retriever")
workflow.add_edge("web_retriever", "grade_web_documents")
workflow.add_conditional_edges(
    "grade_web_documents", # 출발지
    decide_to_websearch,
    {
        "STOP": "generate",
        "RESEARCH": "rewrite_query_with_counter",
    },
)

workflow.add_edge("generate", "grade_generation")

workflow.add_conditional_edges(
    "grade_generation", # 출발지
    decide_to_generate,
    {
        "HALT": END,
        "RETRY": "rewrite_query_without_counter",
    },
)

graph = workflow.compile()