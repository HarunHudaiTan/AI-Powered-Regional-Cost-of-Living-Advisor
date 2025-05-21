# -*- coding: utf-8 -*-


#upload several pdf docs to colab from local machine at once
from google.colab import files
def upload_multiple_files():
  uploaded = files.upload()
  file_names = list()
  for fn in uploaded.keys():
    #print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))
    file_names.append(fn)
  return file_names

file_names = upload_multiple_files()
file_names[0]

# Commented out IPython magic to ensure Python compatibility.
# %pip install pypdf --quiet
from pypdf import PdfReader

def convert_PDF_Text(pdf_path):
  reader = PdfReader(pdf_path)
  pdf_texts = [p.extract_text().strip() for p in reader.pages]
  # Filter the empty strings
  pdf_texts = [text for text in pdf_texts if text]
  print("Document: ",pdf_path," chunk size: ", len(pdf_texts))
  return pdf_texts

pdf_texts = convert_PDF_Text(file_names[0])
pdf_texts[0]

import textwrap
from IPython.display import display
from IPython.display import Markdown
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

to_markdown(pdf_texts[0])

# Commented out IPython magic to ensure Python compatibility.
# %pip install langchain --quiet
import langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

def convert_Page_ChunkinChar(pdf_texts, chunk_size =1000 , chunk_overlap=120 ):
  character_splitter = RecursiveCharacterTextSplitter(
      separators=["\n\n", "\n", ". ", " ", ""],
      chunk_size=1000,
      chunk_overlap=120
)
  character_split_texts = character_splitter.split_text('\n\n'.join(pdf_texts))
  print(f"\nTotal number of chunks (document splited by max char = 1000): \
        {len(character_split_texts)}")
  return character_split_texts

text_chunksinChar = convert_Page_ChunkinChar(pdf_texts)

print("................. NOTICE ..................")
print(file_names[0]," has ", len(pdf_texts), " pages")
print(file_names[0]," has ", len(text_chunksinChar), " chunks")
print("chunk [0] has ", len(text_chunksinChar[0]), " chars")
print("chunk [-1] has ", len(text_chunksinChar[-1]), " chars")

print(text_chunksinChar[0])

# Commented out IPython magic to ensure Python compatibility.
# %pip install sentence_transformers --quiet
# %pip install tqdm --quiet

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
sentence_transformer_model="distiluse-base-multilingual-cased-v1"

def convert_Chunk_Token(text_chunksinChar,sentence_transformer_model, chunk_overlap=10,tokens_per_chunk=128):
  token_splitter = SentenceTransformersTokenTextSplitter(
      chunk_overlap=chunk_overlap,
      model_name=sentence_transformer_model,
      tokens_per_chunk=tokens_per_chunk)

  text_chunksinTokens = []
  for text in text_chunksinChar:
      text_chunksinTokens += token_splitter.split_text(text)
  print(f"\nTotal number of chunks (document splited by 128 tokens per chunk):\
       {len(text_chunksinTokens)}")
  return text_chunksinTokens

from tqdm import tqdm, trange



text_chunksinTokens = convert_Chunk_Token(text_chunksinChar,sentence_transformer_model)

to_markdown(text_chunksinTokens[0])

print("................. NOTICE ..................")
print(file_names[0]," has ", len(pdf_texts), " pages")
print(file_names[0]," has ", len(text_chunksinChar), " chunks splitted by 1500 chars")
print(file_names[0]," has ", len(text_chunksinTokens), " chunks splitted by 128 tokens")
print("text_chunksinChar [0] is:\n ")
display(to_markdown(text_chunksinChar[0]))
print("text_chunksinTokens for the first 3 chunks are:\n ")
display(to_markdown(text_chunksinTokens[0]))
display(to_markdown(text_chunksinTokens[1]))
display(to_markdown(text_chunksinTokens[2]))

# Commented out IPython magic to ensure Python compatibility.
# %pip install chromadb --quiet

import numpy as np
import chromadb
from chromadb.utils import embedding_functions
embedding_function= embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)

chunk=0
print("text (128 token max):\n")
display(to_markdown(text_chunksinTokens[chunk]))
embedding_vector= embedding_function([text_chunksinTokens[chunk]])
print("Embedding Vector shape: ",np.shape(embedding_vector))
print("Embedding Vector dimension: ",len(embedding_vector[0]))
print("Embedding Vector content (for first 5 dimension): \n",embedding_vector[0][0:5])

from chromadb import Client
def create_chroma_client(collection_name, embedding_function):
  chroma_client = Client()
  chroma_collection = chroma_client.get_or_create_collection(collection_name, embedding_function=embedding_function)
  return chroma_client, chroma_collection

collection_name= "UniPrices"
chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)
print(chroma_collection.count())
print(chroma_client.list_collections())

def add_meta_data(text_chunksinTokens, title, category, initial_id):
  ids = [str(i+initial_id) for i in range(len(text_chunksinTokens))]
  metadata = {
      'document': title,
      'category': category
  }
  metadatas = [ metadata for i in range(len(text_chunksinTokens))]
  return ids, metadatas

category="Ankara Uni Price"
ids,metadatas = add_meta_data(text_chunksinTokens,file_names[0],category, 0)
print(len(text_chunksinTokens))
ids[:6], metadatas[:6]

def add_document_to_collection(ids, metadatas, text_chunksinTokens, chroma_collection):
  print("Before inserting, the size of the collection: ", chroma_collection.count())
  chroma_collection.add(ids=ids, metadatas= metadatas, documents=text_chunksinTokens)
  print("After inserting, the size of the collection: ", chroma_collection.count())
  return chroma_collection

chroma_collection = add_document_to_collection(ids, metadatas, text_chunksinTokens, chroma_collection)

chroma_collection.get(['5'])

try:
  chroma_client.delete_collection(collection_name)
  print("Collection deleted successfully.")
except Exception as e:
  print("Error deleting collection:", e)

def load_multiple_pdfs_to_ChromaDB(collection_name,sentence_transformer_model):

  collection_name= collection_name
  category= "Journal Paper"
  sentence_transformer_model=sentence_transformer_model
  embedding_function= embedding_functions.SentenceTransformerEmbeddingFunction(model_name=sentence_transformer_model)
  chroma_client, chroma_collection = create_chroma_client(collection_name, embedding_function)
  current_id = chroma_collection.count()
  file_names = upload_multiple_files()
  for file_name in file_names:
    print(f"Document: {file_name} is being processed to be added to the {chroma_collection.name} {chroma_collection.count()}")
    print(f"current_id: {current_id} ")
    pdf_texts = convert_PDF_Text(file_name)
    text_chunksinChar = convert_Page_ChunkinChar(pdf_texts)
    text_chunksinTokens = convert_Chunk_Token(text_chunksinChar,sentence_transformer_model)
    ids,metadatas = add_meta_data(text_chunksinTokens,file_name,category, current_id)
    current_id = current_id + len(text_chunksinTokens)
    chroma_collection = add_document_to_collection(ids, metadatas, text_chunksinTokens, chroma_collection)
    print(f"Document: {file_name} added to the collection: {chroma_collection.count()}")
  return  chroma_client, chroma_collection

chroma_client, chroma_collection= load_multiple_pdfs_to_ChromaDB(collection_name,sentence_transformer_model)

chroma_collection.get(['0'])

def retrieveDocs(chroma_collection, query, n_results=5, return_only_docs=False):
    results = chroma_collection.query(query_texts=[query],
                                      include= [ "documents","metadatas",'distances' ],
                                      n_results=n_results)

    if return_only_docs:
        return results['documents'][0]
    else:
        return results

query = "Ted Üniversitesi İngilizce Öğretmenliği Programı ücreteri nelerdir?"

results=retrieveDocs(chroma_collection, query, 10)

results

def show_results(results, return_only_docs=False):

  if return_only_docs:
    retrieved_documents = results
    if len(retrieved_documents) == 0:
      print("No results found.")
      return
    for i, doc in enumerate(retrieved_documents):
      print(f"Document {i+1}:")
      print("\tDocument Text: ")
      display(to_markdown(doc));
  else:

      retrieved_documents = results['documents'][0]
      if len(retrieved_documents) == 0:
          print("No results found.")
          return
      retrieved_documents_metadata = results['metadatas'][0]
      retrieved_documents_distances = results['distances'][0]
      print("------- retreived documents -------\n")

      for i, doc in enumerate(retrieved_documents):
          print(f"Document {i+1}:")
          print("\tDocument Text: ")
          display(to_markdown(doc));
          print(f"\tDocument Source: {retrieved_documents_metadata[i]['document']}")
          print(f"\tDocument Source Type: {retrieved_documents_metadata[i]['category']}")
          print(f"\tDocument Distance: {retrieved_documents_distances[i]}")

show_results(results)

# Define your query and desired document
query = "Ted Üniversitesi İngilizce Öğretmenliği Programı ücreteri nelerdir?"
document_filter = "Ted-Universitesi-Egitim-Ucretleri-ve-Burslari-2024-2025.pdf"

results = chroma_collection.query(
    query_texts=[query],
    include=["documents", "metadatas", "distances"],
    where={"document": document_filter},
    n_results=5)

show_results(results)

