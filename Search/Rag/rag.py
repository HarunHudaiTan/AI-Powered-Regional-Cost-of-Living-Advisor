import textwrap
from IPython.display import Markdown, display
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
import chromadb
import os
from chromadb.utils import embedding_functions
from chromadb import Client
from tqdm.notebook import trange, tqdm
from pprint import pprint


# Keep your PDF extraction function as is
def convert_PDF_Text(pdf_path):
    reader = PdfReader(pdf_path)
    pdf_texts = [p.extract_text().strip() for p in reader.pages]
    # Filter the empty strings
    pdf_texts = [text for text in pdf_texts if text]
    print("Document: ", pdf_path, " chunk size: ", len(pdf_texts))
    return pdf_texts


# Helper for displaying text
def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# NEW FUNCTION: Modified chunk creation using sentence-based approach
def create_sentence_chunks(pdf_texts, chunk_size=800, chunk_overlap=200):
    # Combine all PDF texts into one string
    full_text = '\n\n'.join(pdf_texts)

    # Initialize sentence-based text splitter
    sentence_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", ":", ";", ",", " ", ""],  # Process in this order
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    # Split text into chunks based on sentences
    chunks = sentence_splitter.split_text(full_text)

    print(f"\nTotal number of sentence-based chunks: {len(chunks)}")
    return chunks


# The rest of your embedding and collection logic remains the same
sentence_transformer_model = "distiluse-base-multilingual-cased-v1"
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)


def create_chroma_client(collection_name, embedding_function):
    chroma_client = Client()

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


def add_meta_data(chunks, title, category, initial_id):
    ids = [str(i + initial_id) for i in range(len(chunks))]
    filename = os.path.basename(title)
    metadata = {
        'document': filename,
        'category': category
    }
    metadatas = [metadata for i in range(len(chunks))]
    return ids, metadatas


def add_document_to_collection(ids, metadatas, chunks, chroma_collection):
    print("Before inserting, the size of the collection: ", chroma_collection.count())
    chroma_collection.upsert(ids=ids, metadatas=metadatas, documents=chunks)
    print("After inserting, the size of the collection: ", chroma_collection.count())
    return chroma_collection


def retrieveDocs(chroma_collection, query,file,n_results=10, return_only_docs=False):
    results = chroma_collection.query(query_texts=[query],
                                      include=["documents", "metadatas", 'distances'],
                                      where={"document":f"{file}.pdf"},
                                      n_results=n_results)
    if return_only_docs:
        return results['documents'][0]
    else:
        return results


def show_results(results, return_only_docs=False):
    if return_only_docs:
        retrieved_documents = results
        if len(retrieved_documents) == 0:
            print("No results found.")
            return
        for i, doc in enumerate(retrieved_documents):
            print(f"Document {i + 1}:")
            print("\tDocument Text: ")
            pprint(doc)
    else:
        retrieved_documents = results['documents'][0]
        if len(retrieved_documents) == 0:
            print("No results found.")
            return
        retrieved_documents_metadata = results['metadatas'][0]
        retrieved_documents_distances = results['distances'][0]
        print("------- Retrieved documents -------\n")

        for i, doc in enumerate(retrieved_documents):
            print(f"Document {i + 1}:")
            print("\tDocument Text: ")
            pprint(doc)
            # Extract filename from the full path
            full_path = retrieved_documents_metadata[i]['document']
            filename = os.path.basename(full_path)
            print(f"\tDocument Source: {filename}")
            print(f"\tDocument Source Type: {retrieved_documents_metadata[i]['category']}")
            print(f"\tDocument Distance: {retrieved_documents_distances[i]}")
            print("-" * 80)


def list_files_in_directory(directory_path):
    all_entries = os.listdir(directory_path)

    files_only = [entry for entry in all_entries
                  if os.path.isfile(os.path.join(directory_path, entry))]
    return files_only


def get_all_pdf_paths(
        directory_path="/Users/harun/Documents/GitHub/AI-Powered-Regional-Cost-of-Living-Advisor/Search/Rag/Uni_fiyatları"):
    """
    Get all PDF file paths from the specified directory.

    Args:
        directory_path (str): Path to the directory containing PDF files

    Returns:
        list: List of full paths to all PDF files in the directory
    """
    all_files = list_files_in_directory(directory_path)
    pdf_files = [f for f in all_files if f.lower().endswith('.pdf')]
    full_paths = [os.path.join(directory_path, pdf_file) for pdf_file in pdf_files]
    return full_paths


def load_multiple_pdfs_to_ChromaDB(collection_name, sentence_transformer_model):
    """
    Load multiple PDFs into ChromaDB collection with proper chunking and embedding.

    Args:
        collection_name (str): Name of the ChromaDB collection
        sentence_transformer_model (str): Name of the sentence transformer model to use
        chromaDB_path (str, optional): Path to store ChromaDB data. Defaults to None.

    Returns:
        tuple: (chroma_client, chroma_collection)
    """
    # Initialize embedding function
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)

    # Create or get ChromaDB client and collection
    chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)

    # Get current ID for continuous indexing
    current_id = chroma_collection.count()

    # Get all PDF paths from the directory
    pdf_paths = get_all_pdf_paths()

    for pdf_path in pdf_paths:
        # Extract text from PDF
        pdf_texts = convert_PDF_Text(pdf_path)

        # Create sentence-based chunks
        chunks = create_sentence_chunks(pdf_texts)

        # Add metadata and get IDs
        ids, metadatas = add_meta_data(chunks, pdf_path, "PricePaper", current_id)

        # Update current_id for next document
        current_id += len(chunks)

        # Add to collection
        chroma_collection = add_document_to_collection(ids, metadatas, chunks, chroma_collection)

        print(f"Document: {pdf_path} added to the collection. New size: {chroma_collection.count()}")

    return chroma_client, chroma_collection


import KeywordAgent as keyword_agent

chroma_client, chroma_collection = load_multiple_pdfs_to_ChromaDB("UniPrices", sentence_transformer_model)
query = " lokman hekim üniversitesi yaşlı bakımı ücretleri"
keyword = keyword_agent.parse_keywords(query)
filtered_keyword=keyword.strip('"')
retrieved_documents = retrieveDocs(chroma_collection, query,filtered_keyword,10)
show_results(retrieved_documents)

