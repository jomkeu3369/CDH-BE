from typing import Annotated, Optional, List, TypedDict

class MainState(TypedDict):
    counter: Annotated[int, "웹 검색 수 (최대 5)"]
    note_id: int
    user_id: int
    original_query: str
    optimize_query: Optional[str]
    generation: Annotated[Optional[str], "LLM이 생성한 최종 답변"]
    self_rag: bool
    self_rag_counter: int
    api_query: Optional[str]
    erd_query: Optional[str]
    vector_store_context: List[str]
    web_search_context: List[str]