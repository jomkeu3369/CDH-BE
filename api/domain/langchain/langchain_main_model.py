from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

prompt = PromptTemplate.from_template(template)

model = ChatOpenAI(
    model="gpt-4o",
    max_tokens=2048,
    temperature=0.1,
)

chain = prompt | model | output_parser