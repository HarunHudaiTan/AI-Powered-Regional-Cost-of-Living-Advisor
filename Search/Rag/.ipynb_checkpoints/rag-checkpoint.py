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
    # existing_collections = [col.name for col in chroma_client.list_collections()]
    # if collection_name in existing_collections:
    #   print(f"Deleting existing collection: {collection_name}")
    #   chroma_client.delete_collection(collection_name)
    #
    # Create a new collection
    chroma_collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

    return chroma_client, chroma_collection


def add_meta_data(chunks, title, category, initial_id):
    ids = [str(i + initial_id) for i in range(len(chunks))]
    metadata = {
        'document': title,
        'category': category
    }
    metadatas = [metadata for i in range(len(chunks))]
    return ids, metadatas


def add_document_to_collection(ids, metadatas, chunks, chroma_collection):
    print("Before inserting, the size of the collection: ", chroma_collection.count())
    chroma_collection.upsert(ids=ids, metadatas=metadatas, documents=chunks)
    print("After inserting, the size of the collection: ", chroma_collection.count())
    return chroma_collection


def retrieveDocs(chroma_collection, query, n_results=10, return_only_docs=False):
    results = chroma_collection.query(query_texts=[query],
                                      include=["documents", "metadatas", 'distances'],
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
            display(to_markdown(doc))
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
            display(to_markdown(doc))
            print(f"\tDocument Source: {retrieved_documents_metadata[i]['document']}")
            print(f"\tDocument Source Type: {retrieved_documents_metadata[i]['category']}")
            print(f"\tDocument Distance: {retrieved_documents_distances[i]}")
            print("-" * 80)



def list_files_in_directory(directory_path):
    all_entries = os.listdir(directory_path)

    files_only = [entry for entry in all_entries
                  if os.path.isfile(os.path.join(directory_path, entry))]
    return files_only

pdf_paths=list_files_in_directory("/Users/harun/Documents/GitHub/AI-Powered-Regional-Cost-of-Living-Advisor/Search/Rag/Uni_fiyatları/")

for pdf_path in pdf_paths:
    pdf_text = convert_PDF_Text("/Users/harun/Documents/GitHub/AI-Powered-Regional-Cost-of-Living-Advisor/Search/Rag/Uni_fiyatları/"+f"{pdf_path}")


chunks=create_sentence_chunks(pdf_text)
chroma_client,chroma_collection=create_chroma_client("UniPrices", embedding_function)
ids,metadatas=add_meta_data(chunks, f"{pdf_text}", "PricePaper", 0)
chroma_collection=add_document_to_collection(ids, metadatas, chunks, chroma_collection)
query="Mühendislik Fakültesi fiyatları"
results = retrieveDocs(chroma_collection, query)
print(results)

    # file_path = "/Users/harun/Documents/GitHub/AI-Powered-Regional-Cost-of-Living-Advisor/Search/Rag/Uni_fiyatları/mudanyaUniversitesi.pdf
    #"
    # # Extract text from PDF
    # pdf_texts = convert_PDF_Text(file_path)
    #
    # # Print one of the extracted pages to see content
    # print("\nSample of extracted text:")
    # print(pdf_texts[0][:500] + "...")
    #
    # # Create sentence-based chunks instead of character-based chunks
    # text_chunks = create_sentence_chunks(pdf_texts, chunk_size=800, chunk_overlap=300)
    #
    # # Print a few chunks to verify the chunking
    # print("\nSample chunks:")
    # for i in range(min(3, len(text_chunks))):
    #     print(f"Chunk {i + 1}:")
    #     print(text_chunks[i][:200] + "...")
    #
    # # Initialize Chroma client and collection
    # collection_name = "UniPrices"
    # chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)
    #
    # # Add metadata
    # category = "Ankara Uni Price"
    # ids, metadatas = add_meta_data(text_chunks, file_path, category, 0)
    #
    # # Add to collection
    # chroma_collection = add_document_to_collection(ids, metadatas, text_chunks, chroma_collection)
    #
    # # Search example
    # query = "Mühendislik Fakültesi ücretleri?"
    # results = retrieveDocs(chroma_collection, query, n_results=10)
    #
    # # Print all results
    # print("\nAll search results:")
    # show_results(results)

    # # Filter results with distances below 1 (more relevant)
    # filtered_documents = []
    # filtered_metadatas = []
    # filtered_distances = []
    #
    # for i, distance in enumerate(results['distances'][0]):
    #     if distance < 1.0:  # Only keep documents with distance less than 1
    #         filtered_documents.append(results['documents'][0][i])
    #         filtered_metadatas.append(results['metadatas'][0][i])
    #         filtered_distances.append(distance)
    #
    # # Create a new results dictionary with filtered data
    # filtered_results = {
    #     'documents': [filtered_documents],
    #     'metadatas': [filtered_metadatas],
    #     'distances': [filtered_distances]
    # }
    #
    # # Print filtered results
    # print("\nFiltered search results (distance < 1.0):")
    # print(f"Original results: {len(results['documents'][0])}")
    # print(f"Filtered results: {len(filtered_documents)}")
    # show_results(filtered_results)
    #
