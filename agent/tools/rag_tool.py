import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(
    name="policy_docs", embedding_function=ef
)

def load_policy(text: str):
    # chunk into 200-char pieces
    chunks = [text[i:i+200] for i in range(0, len(text), 200)]
    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return {"loaded_chunks": len(chunks)}

def retrieve_context(query: str, n=3) -> str:
    results = collection.query(query_texts=[query], n_results=min(n, collection.count()))
    docs = results.get("documents", [[]])[0]
    return "\n".join(docs) if docs else "No context found."