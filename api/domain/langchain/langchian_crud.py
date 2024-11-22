import os
from dotenv import load_dotenv
from fastapi import UploadFile
from typing import IO
from tempfile import NamedTemporaryFile

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document

from api.models.ORM import UserInfo

load_dotenv()

async def save_file(file: IO, extension: str):
    file_content = (file.read()).decode("utf-8")

    with NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=f".{extension}") as tempfile:
        tempfile.write(file_content)
        return tempfile.name
    
async def upload_file(user: UserInfo, file: UploadFile):
    filename = file.filename
    extension = filename.split(".")[-1] if "." in filename else "txt"

    path = await save_file(file.file, extension)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=0)
    loader = TextLoader(path, encoding="utf-8")
    split_doc = loader.load_and_split(text_splitter)

    db = FAISS.load_local(
        folder_path=os.getenv("DB_path"),
        index_name="faiss_index",
        embeddings=OpenAIEmbeddings(),
        allow_dangerous_deserialization=True,
    )

    for doc in split_doc:
        updated_metadata = doc.metadata.copy()
        updated_metadata["user_id"] = user.user_id
        
        db.add_documents(
            [
                Document(
                    page_content=doc.page_content,
                    metadata=updated_metadata,
                )
            ]
        )

    db.save_local(folder_path=os.getenv("DB_path"), index_name="faiss_index")
    os.remove(path)