from app.config import HF_TOKEN
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
import numpy as np

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    model_kwargs={"token": HF_TOKEN},
    encode_kwargs={"normalize_embeddings": True}
)

vector_cache = {}
bm25_cache = {}

def build_index(video_id: str):
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=["en"])

    docs = []
    raw_texts = []

    for chunk in transcript:
        text = chunk.text
        metadata = {"timestamp": chunk.start}
        docs.append(Document(page_content=text, metadata=metadata))
        raw_texts.append(text.split())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    split_docs = splitter.split_documents(docs)

    vectorstore = FAISS.from_documents(split_docs, embedding_model)
    bm25 = BM25Okapi([doc.page_content.split() for doc in split_docs])

    vector_cache[video_id] = vectorstore
    bm25_cache[video_id] = (bm25, split_docs)


def get_full_transcript(video_id: str):
    if video_id not in vector_cache:
        build_index(video_id)

    # Return all split docs
    _, docs = bm25_cache[video_id]
    return docs


def hybrid_retrieve(video_id: str, query: str, k: int = 8):
    if video_id not in vector_cache:
        build_index(video_id)

    vectorstore = vector_cache[video_id]
    bm25, docs = bm25_cache[video_id]

    # Semantic retrieval
    semantic_docs = vectorstore.similarity_search(query, k=k)

    # BM25 retrieval
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[-k:]
    bm25_docs = [docs[i] for i in top_indices]

    # Combine & deduplicate
    combined = {doc.page_content: doc for doc in semantic_docs + bm25_docs}

    return list(combined.values())