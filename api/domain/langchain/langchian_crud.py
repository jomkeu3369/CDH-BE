import os
from dotenv import load_dotenv
from fastapi import UploadFile
from typing import IO
from tempfile import NamedTemporaryFile

from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from api.domain.langchain import langchain_DB
from langchain_core.documents import Document

from api.models.ORM import UserInfo

load_dotenv()

async def save_file(file: IO, extension: str):
    # file_content = file.read()

    with NamedTemporaryFile("wb", delete=False, suffix=f".{extension}") as tempfile:
        tempfile.write(file.read())
        return tempfile.name

    # with NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=f".{extension}") as tempfile:
    #     tempfile.write(file_content)
    #     return tempfile.name

async def process_file(file_path: str):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".csv"):
        loader = CSVLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다 : {file_path}")
    
    return loader

async def upload_file(user: UserInfo, note_id: int, file: UploadFile):
    filename = file.filename
    extension = filename.split(".")[-1] if "." in filename else "txt"

    path = await save_file(file.file, extension)
    documents = await process_file(path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=200)
    split_doc = documents.load_and_split(text_splitter)

    db = langchain_DB.db

    for doc in split_doc:
        updated_metadata = doc.metadata.copy()
        updated_metadata["user_id"] = user.user_id
        updated_metadata["note_id"] = note_id
        
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