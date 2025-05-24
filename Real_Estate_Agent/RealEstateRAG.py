import os
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
import numpy as np
from typing import List, Dict, Any
import textwrap
import tkinter as tk
from tkinter import filedialog

def convert_PDF_Text(pdf_path):
    reader = PdfReader(pdf_path)
    pdf_texts = [p.extract_text().strip() for p in reader.pages]
    # Filter the empty strings
    pdf_texts = [text for text in pdf_texts if text]
    print("Document: ", pdf_path, " chunk size: ", len(pdf_texts))
    return pdf_texts

def convert_Page_ChunkinChar(pdf_texts, chunk_size=700, chunk_overlap=100):
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    character_split_texts = character_splitter.split_text('\n\n'.join(pdf_texts))
    print(f"\nTotal number of chunks (document split by max char = {chunk_size}): {len(character_split_texts)}")
    return character_split_texts

def convert_Chunk_Token(text_chunksinChar, sentence_transformer_model, chunk_overlap=20, tokens_per_chunk=128):
    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=chunk_overlap,
        model_name=sentence_transformer_model,
        tokens_per_chunk=tokens_per_chunk
    )

    text_chunksinTokens = []
    for text in text_chunksinChar:
        text_chunksinTokens += token_splitter.split_text(text)
    print(f"\nTotal number of chunks (document split by {tokens_per_chunk} tokens per chunk): {len(text_chunksinTokens)}")
    return text_chunksinTokens

def create_chroma_client(collection_name, embedding_function, persist_directory="./chroma_db"):
    """
    Create a persistent ChromaDB client and collection.
    
    Args:
        collection_name (str): Name of the collection
        embedding_function: Function to create embeddings
        persist_directory (str): Directory where ChromaDB stores its data
        
    Returns:
        tuple: (chroma_client, chroma_collection)
    """

    absolute_path = os.path.abspath(persist_directory)  # Get the absolute path
    print(f"ChromaDB will persist data in: {absolute_path}")  # Print it
    # Create a persistent client that stores data in the persist_directory
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    chroma_collection = chroma_client.get_or_create_collection(collection_name, embedding_function=embedding_function)
    return chroma_client, chroma_collection

def show_database_info(chroma_client, collection_name):
    """
    Display information about the ChromaDB database.
    
    Args:
        chroma_client: ChromaDB client
        collection_name (str): Name of the collection
    """
    print("\nDatabase Information:")
    print("-" * 40)
    print(f"Database Location: {os.path.abspath('chroma_db')}")
    print(f"Collection Name: {collection_name}")
    print(f"Total Chunks: {chroma_client.get_collection(collection_name).count()}")
    print("-" * 40)

def add_meta_data(text_chunksinTokens, title, category, initial_id):
    ids = [str(i+initial_id) for i in range(len(text_chunksinTokens))]
    metadata = {
        'document': title,
        'category': category
    }
    metadatas = [metadata for i in range(len(text_chunksinTokens))]
    return ids, metadatas

def add_document_to_collection(ids, metadatas, text_chunksinTokens, chroma_collection):
    print("Before inserting, the size of the collection: ", chroma_collection.count())
    chroma_collection.add(ids=ids, metadatas=metadatas, documents=text_chunksinTokens)
    print("After inserting, the size of the collection: ", chroma_collection.count())
    return chroma_collection

def load_multiple_pdfs_to_ChromaDB(collection_name, sentence_transformer_model, pdf_directory, category="Document"):
    """
    Load multiple PDFs from a directory into ChromaDB with persistent storage.
    
    Args:
        collection_name (str): Name of the ChromaDB collection
        sentence_transformer_model (str): Name of the sentence transformer model to use
        pdf_directory (str): Directory containing PDF files to process
        category (str): Category to assign to the documents
    """
    # Create embedding function
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)
    
    # Create persistent client and collection
    chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)
    current_id = chroma_collection.count()
    
    # Get list of PDF files from directory
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    
    for file_name in pdf_files:
        file_path = os.path.join(pdf_directory, file_name)
        print(f"Document: {file_name} is being processed to be added to the {chroma_collection.name} {chroma_collection.count()}")
        print(f"current_id: {current_id}")
        
        # Process the PDF
        pdf_texts = convert_PDF_Text(file_path)
        text_chunksinChar = convert_Page_ChunkinChar(pdf_texts)
        text_chunksinTokens = convert_Chunk_Token(text_chunksinChar, sentence_transformer_model)
        
        # Add to collection
        ids, metadatas = add_meta_data(text_chunksinTokens, file_name, category, current_id)
        current_id = current_id + len(text_chunksinTokens)
        chroma_collection = add_document_to_collection(ids, metadatas, text_chunksinTokens, chroma_collection)
        print(f"Document: {file_name} added to the collection: {chroma_collection.count()}")
    
    return chroma_client, chroma_collection

def format_chunk(chunk: str, width: int = 80) -> str:
    """
    Format a text chunk to be more readable with proper wrapping and indentation.
    
    Args:
        chunk (str): The text chunk to format
        width (int): The maximum width of each line
        
    Returns:
        str: Formatted text chunk
    """
    # Remove extra whitespace and normalize line endings
    chunk = ' '.join(chunk.split())
    
    # Wrap the text
    wrapped_text = textwrap.fill(chunk, width=width)
    
    # Add indentation
    indented_text = textwrap.indent(wrapped_text, '    ')
    
    return indented_text

def display_chunks(results: Dict[str, Any], max_chunks: int = 5) -> None:
    """
    Display chunks from Real_Estate_RAG results in a readable format.
    
    Args:
        results (Dict[str, Any]): Results from ChromaDB query
        max_chunks (int): Maximum number of chunks to display
    """
    if not results['documents'][0]:
        print("No chunks found matching the query.")
        return
        
    print("\n" + "="*80)
    print("Real_Estate_RAG CHUNKS FROM QUERY")
    print("="*80 + "\n")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0][:max_chunks],
        results['metadatas'][0][:max_chunks],
        results['distances'][0][:max_chunks]
    )):
        print(f"\nCHUNK {i+1}")
        print("-"*40)
        print(f"Source: {metadata['document']}")
        print(f"Category: {metadata['category']}")
        print(f"Distance: {distance:.4f}")  # Show actual distance value
        print("\nContent:")
        print(format_chunk(doc))
        print("-"*40)
    
    if len(results['documents'][0]) > max_chunks:
        print(f"\n... and {len(results['documents'][0]) - max_chunks} more chunks")

def show_results(results):
    """
    Display Real_Estate_RAG results in a readable format.
    
    Args:
        results (List[Dict]): List of result dictionaries containing 'document' and 'metadata' keys
    """
    if not results:
        print("No results found.")
        return
        
    print("\n" + "="*80)
    print("Real_Estate_RAG RESULTS")
    print("="*80 + "\n")
    
    for i, result in enumerate(results):
        print(f"\nRESULT {i+1}")
        print("-"*40)
        print(f"Source: {result['metadata']['document']}")
        print(f"Category: {result['metadata']['category']}")
        print("\nContent:")
        print(format_chunk(result['document']))
        print("-"*40)

def retrieveDocs(chroma_collection, query, n_results=5):
    """
    Retrieve documents from ChromaDB based on a query.
    
    Args:
        chroma_collection: ChromaDB collection to query
        query (str): The search query
        n_results (int): Number of results to return
        
    Returns:
        List[Dict]: List of dictionaries containing 'document' and 'metadata' keys
    """
    results = chroma_collection.query(
        query_texts=[query],
        include=["documents", "metadatas", 'distances'],
        n_results=n_results
    )

    # Format results into a list of dictionaries
    formatted_results = []
    for doc, metadata, distance in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        formatted_results.append({
            'document': doc,
            'metadata': metadata,
            'distance': distance
        })
    
    return formatted_results

def select_pdf_files() -> List[str]:
    """
    Open a file dialog to select PDF files.
    
    Returns:
        List[str]: List of selected PDF file paths
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    print("\nPlease select the PDF files you want to add to the Real_Estate_RAG system...")
    file_paths = filedialog.askopenfilenames(
        title="Select PDF files",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    
    if not file_paths:
        print("No files were selected.")
        return []
        
    print(f"\nSelected {len(file_paths)} files:")
    for i, path in enumerate(file_paths, 1):
        print(f"{i}. {os.path.basename(path)}")
    
    return list(file_paths)

def delete_document_from_collection(chroma_collection, document_name):
    """
    Delete all chunks of a specific document from the ChromaDB collection.
    
    Args:
        chroma_collection: ChromaDB collection
        document_name (str): Name of the document to delete
        
    Returns:
        int: Number of chunks deleted
    """
    try:
        # Get all documents with matching metadata
        results = chroma_collection.get(
            where={"document": document_name}
        )
        
        if not results['ids']:
            print(f"No document found with name: {document_name}")
            return 0
            
        # Delete the documents
        chroma_collection.delete(
            ids=results['ids']
        )
        
        deleted_count = len(results['ids'])
        print(f"Successfully deleted {deleted_count} chunks from document: {document_name}")
        return deleted_count
        
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return 0

def delete_all_documents_from_collection(chroma_collection):
    """
    Delete all documents from the ChromaDB collection.
    
    Args:
        chroma_collection: ChromaDB collection
        
    Returns:
        int: Number of chunks deleted
    """
    try:
        # Get all documents
        results = chroma_collection.get()
        
        if not results['ids']:
            print("No documents found in the collection.")
            return 0
            
        # Delete all documents
        chroma_collection.delete(
            ids=results['ids']
        )
        
        deleted_count = len(results['ids'])
        print(f"Successfully deleted all {deleted_count} chunks from the collection")
        return deleted_count
        
    except Exception as e:
        print(f"Error deleting documents: {str(e)}")
        return 0

if __name__ == "__main__":
    # Example usage
    collection_name = "MyDocuments"
    sentence_transformer_model = "distiluse-base-multilingual-cased-v1"
    
    # Create embedding function and client first
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)
    chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)
    
    # Show database information
    show_database_info(chroma_client, collection_name)
    
    # Select PDF files
    pdf_files = select_pdf_files()
    
    # Process new files if any were selected
    if pdf_files:
        print("\nLoading new PDFs into ChromaDB...")
        try:
            current_id = chroma_collection.count()
            
            # Process each selected PDF file
            for file_path in pdf_files:
                file_name = os.path.basename(file_path)
                print(f"\nProcessing: {file_name}")
                print(f"Current collection size: {chroma_collection.count()}")
                
                # Process the PDF
                pdf_texts = convert_PDF_Text(file_path)
                text_chunksinChar = convert_Page_ChunkinChar(pdf_texts)
                text_chunksinTokens = convert_Chunk_Token(text_chunksinChar, sentence_transformer_model)
                
                # Add to collection
                ids, metadatas = add_meta_data(text_chunksinTokens, file_name, "Selected Document", current_id)
                current_id = current_id + len(text_chunksinTokens)
                chroma_collection = add_document_to_collection(ids, metadatas, text_chunksinTokens, chroma_collection)
                print(f"Added {file_name} to the collection")
                
            # Show updated database information after adding new files
            show_database_info(chroma_client, collection_name)
            
        except Exception as e:
            print(f"Error processing new files: {str(e)}")
    
    # Show current collection status
    total_docs = chroma_collection.count()
    if total_docs == 0:
        print("\nNo documents in the collection. Please select some PDF files to process.")
        exit(1)
    else:
        print(f"\nCurrent collection status: {total_docs} chunks from existing documents")
    
    # Run query on existing documents
    try:
        query = "Samsun su tarifesi"
        print(f"\nQuerying with: {query}")
        results = retrieveDocs(chroma_collection, query, n_results=5)
        show_results(results)
        
    except Exception as e:
        print(f"Error querying documents: {str(e)}")
        print("\nMake sure you have:")
        print("1. Installed all required packages: pip install -r requirements.txt")
        print("2. Have enough disk space for the ChromaDB database")

