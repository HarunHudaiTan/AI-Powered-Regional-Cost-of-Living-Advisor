import sys
import os

# Add the RAG directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RealEstateAgent.RAG.RealEstateRAG import (
    create_chroma_client,
    show_database_info,
    delete_all_documents_from_collection
)
from chromadb.utils import embedding_functions

def main():
    # Initialize ChromaDB
    collection_name = "MyDocuments"
    sentence_transformer_model = "distiluse-base-multilingual-cased-v1"
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)
    
    print("Initializing ChromaDB connection...")
    chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)
    
    # Show initial database information
    print("\nInitial database status:")
    show_database_info(chroma_client, collection_name)
    
    # Delete all documents
    print("\nDeleting all documents from the collection...")
    deleted_count = delete_all_documents_from_collection(chroma_collection)
    
    # Show final database information
    print("\nFinal database status:")
    show_database_info(chroma_client, collection_name)
    
    if deleted_count > 0:
        print(f"\nSuccessfully deleted {deleted_count} chunks from the collection.")
    else:
        print("\nNo documents were found to delete.")

if __name__ == "__main__":
    main() 