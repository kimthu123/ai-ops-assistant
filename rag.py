import os
import voyageai
import chromadb

voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="tickets")

def get_embedding(text: str) -> list[float]:
    result = voyage_client.embed([text], model="voyage-3")
    return result.embeddings[0]

def add_ticket_to_index(ticket_id: int, title: str, description: str):
    text = f"{title} {description}"
    embedding = get_embedding(text)
    collection.add(
        ids=[str(ticket_id)],
        embeddings=[embedding],
        documents=[text]
    )

def find_similar_tickets(title: str, description: str, n_results: int = 3):
    text = f"{title} {description}"
    embedding = get_embedding(text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    return results