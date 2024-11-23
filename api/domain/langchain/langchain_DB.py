from dotenv import load_dotenv
import os

from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings

load_dotenv()
DB_PATH = os.getenv("DB_path")

db = FAISS.load_local(
        folder_path=DB_PATH,
        index_name="faiss_index",
        embeddings=OpenAIEmbeddings(),
        allow_dangerous_deserialization=True,
    )