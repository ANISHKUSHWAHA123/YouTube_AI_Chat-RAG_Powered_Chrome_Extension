from app.config import HF_TOKEN
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-Coder-Next",
    temperature=0.1,
    max_new_tokens=300,
    huggingfacehub_api_token=HF_TOKEN,
    return_full_text=False
)

model = ChatHuggingFace(llm=llm)

faithfulness_prompt = PromptTemplate(
    template="""
You are a strict evaluator.

Context:
{context}

Answer:
{answer}

List unsupported claims.
Return JSON:

{{
    "unsupported_statements": [],
    "score": float
}}
""",
    input_variables=["context", "answer"]
)

def evaluate(context: str, answer: str):
    chain = faithfulness_prompt | model | StrOutputParser()
    return chain.invoke({"context": context, "answer": answer})