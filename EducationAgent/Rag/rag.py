import textwrap
from IPython.display import Markdown, display
from langchain_text_splitters import SentenceTransformersTokenTextSplitter
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import os
from chromadb.utils import embedding_functions


# Keep your PDF extraction function as is
def convert_PDF_Text(pdf_path):
    reader = PdfReader(pdf_path)
    pdf_texts = [p.extract_text().strip() for p in reader.pages]
    # Filter the empty strings
    pdf_texts = [text for text in pdf_texts if text]
    return pdf_texts


# Helper for displaying text
def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# NEW FUNCTION: Modified chunk creation using sentence-based approach
def text_Chunks_in_Char(pdf_texts, chunk_size=800, chunk_overlap=100):
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
    return chunks


def convert_Chunk_Token(text_chunksinChar, sentence_transformer_model, chunk_overlap=10, tokens_per_chunk=128):
    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=chunk_overlap,
        model_name=sentence_transformer_model,
        tokens_per_chunk=tokens_per_chunk)

    text_chunksinTokens = []
    for text in text_chunksinChar:
        text_chunksinTokens += token_splitter.split_text(text)
    print(f"\nTotal number of chunks (document splited by 128 tokens per chunk): {len(text_chunksinTokens)}")
    return text_chunksinTokens


# The rest of your embedding and collection logic remains the same
sentence_transformer_model = "distiluse-base-multilingual-cased-v1"
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)


def create_chroma_client(collection_name, embedding_function):
    chroma_client = chromadb.PersistentClient()

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
    chroma_collection.upsert(ids=ids, metadatas=metadatas, documents=chunks)
    return chroma_collection


def retrieveDocs(chroma_collection, query, file=None, n_results=10, return_only_docs=False):

    # Build query parameters
    query_params = {
        "query_texts": [query],
        "include": ["documents", "metadatas", 'distances'],
        "n_results": n_results
    }

    # Add file filter if provided
    if file is not None:
        query_params["where"] = {"document": f"{file}.pdf"}

    # Execute the query
    results = chroma_collection.query(**query_params)
    print(results['distances'])
    if return_only_docs:
        return results['documents'][0]
    else:
        return results

def show_results(results, return_only_docs=False):
    if return_only_docs:
        retrieved_documents = results

        if len(retrieved_documents) == 0:
            return []
        # Format each document with a bullet point
        formatted_docs = [f"• {doc}" for doc in retrieved_documents]
        return "\n".join(formatted_docs)
    else:
        retrieved_documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        if len(retrieved_documents) == 0:
            return []
            
        # Format each document with source information
        formatted_docs = []
        for doc, metadata in zip(retrieved_documents, metadatas):
            # Clean up the document text by removing extra spaces and [UNK] tokens
            cleaned_doc = doc.replace('[UNK]', '').strip()
            # Add proper spacing between sentences
            cleaned_doc = '. '.join(s.strip() for s in cleaned_doc.split('.') if s.strip())
            formatted_doc = f"• {cleaned_doc}\n  From: {metadata['document']}\n"
            formatted_docs.append(formatted_doc)
        return "\n".join(formatted_docs)


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

        # Create character-based chunks first
        char_chunks = text_Chunks_in_Char(pdf_texts)
        
        # Convert to token-based chunks
        token_chunks = convert_Chunk_Token(char_chunks, sentence_transformer_model)

        # Add metadata and get IDs
        ids, metadatas = add_meta_data(token_chunks, pdf_path, "PricePaper", current_id)

        # Update current_id for next document
        current_id += len(token_chunks)

        # Add to collection
        chroma_collection = add_document_to_collection(ids, metadatas, token_chunks, chroma_collection)

    return chroma_client, chroma_collection


def get_existing_chroma_collection(collection_name):

    chroma_client = chromadb.PersistentClient()
    
    # Get the existing collection
    chroma_collection = chroma_client.get_collection(
        name=collection_name
    )
    
    return  chroma_collection


from KeywordAgent import parse_university_keywords

# university_dictionary=parse_university_keywords("Oğlumu Ostim Teknik Üniversitesinde Fizyoterapi bölümünde Okutmak istiyorum Fiyatları nelerdir")
# university_name=university_dictionary["university_name"]
# department=university_dictionary["department"]
# print(department)
# chroma_collection = get_existing_chroma_collection("UniPrices")
# query = department+"Ücretleri"
# retrieved_documents = retrieveDocs(chroma_collection, query, university_name, 10, return_only_docs=True)
# print(show_results(retrieved_documents,return_only_docs=True))

def rag_Response(query):
    chroma_collection=get_existing_chroma_collection("UniPrices")
    university_dictionary = parse_university_keywords(query)
    university_name = university_dictionary["university_name"]
    department = university_dictionary["department"]
    rag_query = department + "Ücretleri"
    retrieved_documents = retrieveDocs(chroma_collection, rag_query, university_name, 10,return_only_docs=True)
    print(show_results(retrieved_documents, return_only_docs=True))
    return show_results(retrieved_documents, return_only_docs=True)

