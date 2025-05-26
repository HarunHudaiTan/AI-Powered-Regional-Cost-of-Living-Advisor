import os

import chromadb
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


def create_chroma_client(collection_name, model_name):
    chroma_client = chromadb.PersistentClient()

    embedding_function = SentenceTransformerEmbeddingFunction(model_name=model_name)

    # Check if collection already exists and delete it
    existing_collections = [col.name for col in chroma_client.list_collections()]
    if collection_name in existing_collections:
        chroma_client.delete_collection(collection_name)

    # Create a new collection
    chroma_collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

    return chroma_client, chroma_collection


def add_document_to_collection(ids, metadatas, chunks, chroma_collection):
    chroma_collection.add(ids=ids, metadatas= metadatas, documents=chunks)
    return chroma_collection


def retrieveDocs(chroma_collection, query, city_name, n_results=1, return_only_docs=False):

    # Build query parameters
    query_params = {
        "query_texts": [query],
        "include": ["documents", "metadatas", 'distances'],
        "n_results": n_results,
        "where": {"city": city_name}
    }

    # Execute the query
    results = chroma_collection.query(**query_params)

    if return_only_docs:
        return results['documents'][0]
    else:
        return results


def get_existing_chroma_collection( collection_name):
    # Create embedding function only when needed for existing collections
    sentence_transformer_model = "distiluse-base-multilingual-cased-v1"
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=sentence_transformer_model)

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chroma_db_path = os.path.join(script_dir, "chroma")

    chroma_client = chromadb.PersistentClient(path=chroma_db_path)

    # Get the existing collection
    chroma_collection = chroma_client.get_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

    return chroma_collection

def public_transport_rag_Response(query, city_name):
    chroma_collection=get_existing_chroma_collection("Transportation_Prices")
    retrieved_documents = retrieveDocs(chroma_collection, query, city_name, return_only_docs=True)
    return retrieved_documents
