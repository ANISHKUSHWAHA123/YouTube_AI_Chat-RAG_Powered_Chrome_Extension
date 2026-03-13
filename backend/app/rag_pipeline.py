from app.config import HF_TOKEN
from app.retriever import hybrid_retrieve, get_full_transcript
from app.memory import load_memory, save_memory
from app.evaluator import evaluate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint



llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-Coder-Next",
    temperature=0.3,
    max_new_tokens=700,
    huggingfacehub_api_token=HF_TOKEN,
    return_full_text=False
)

model = ChatHuggingFace(llm=llm)


prompt = PromptTemplate(
    template="""
You are an intelligent YouTube AI assistant.

Your job:
- Answer questions using ONLY the transcript context provided.
- Adapt to different question styles (summary, themes, explanation, opinion, fact lookup).
- Be helpful but NEVER hallucinate.
- If transcript does not contain enough information, say:
  "I don't know based on this video."

Conversation Memory:
{memory}

Transcript Context:
{context}

User Question:
{question}

Answer:
""",
    input_variables=["memory", "context", "question"]
)


def detect_query_type(question: str):
    q = question.lower()

    if "summarize" in q or "summary" in q:
        return "summary"
    elif "theme" in q or "topics" in q:
        return "themes"
    elif "list" in q:
        return "list"
    else:
        return "qa"


def process_query(video_id: str, question: str, session_id: str):

    query_type = detect_query_type(question)

    if query_type == "summary":
        # For summary → use full transcript
        docs = get_full_transcript(video_id)
    else:
        # For normal Q&A → use hybrid retrieval
        docs = hybrid_retrieve(video_id, question, k=8)

    context = "\n\n".join(
        f"[{doc.metadata.get('timestamp',0):.1f}s] {doc.page_content}"
        for doc in docs
    )

    memory = load_memory(session_id)

    chain = prompt | model | StrOutputParser()

    answer = chain.invoke({
        "memory": memory,
        "context": context,
        "question": question
    })

    save_memory(session_id, answer[:300])

    faithfulness = evaluate(context, answer)

    return {
        "answer": answer,
        "faithfulness": faithfulness
    }
    
    