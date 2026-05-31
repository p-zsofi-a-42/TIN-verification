# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    processing_files.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/05 19:58:55 by zpalotas          #+#    #+#              #
#    Updated: 2026/05/31 20:03:42 by zpalotas         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python
# coding: utf-8

# IMPORT LANGCHAIN MODULES
from langchain_community.document_loaders import PyPDFLoader
	# reads PDF files and turns them into text langchain can work with
from langchain_text_splitters import RecursiveCharacterTextSplitter
	# cuts that text into smaller chunks (AI can't read huge docs in one go)
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
	# Gemini embeddings model and a chat model
from langchain_community.vectorstores import Chroma
	# a local database that stores your chunks in a searchable way
from langchain_core.prompts import ChatPromptTemplate
	# lets you write a template for how to instruct the AI
from pydantic import BaseModel, Field
	# used for defining structured/typed outputs - fairly advanced
from langchain_classic.evaluation import load_evaluator
	# used for embedding evaluation
from langchain_chroma import Chroma
	# used for loading vector storage

# OTHER PACKAGES
import uuid
	# generate unique random IDs
from IPython.display import display
	# dosplays tables in a nice way
import json
	# reads and writes JSON files (key-value storage)

# MY FUNCTIONS
from llm_config			import llm, get_embedding

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Prompt instructions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PROMPT_TEMPLATE = r"""
Use the following pieces of retieved information only to answer the question
If you don't know the answer, say "I don't know", Don't make up anything.

{context}

Answer based on the above context: {question}

Return regex patterns as valid Python regex strings.
Example: 9 digits only -> ["^\\d{{9}}$"]
Example: starts with T followed by 8 digits -> ["^T\\d{{8}}$"]
Do not use [A-Z] unless any letter is explicitly valid.
Verify each pattern mentally against the document rules before returning.
"""
prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Answer template
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# pydantic is a data validation lib for python. to specify the stucture of the answer
class structuredAnswer(BaseModel):
		answer: str = Field(description="TIN structure answer in a very plain format, just describe the rules shortly, no narrative text")
		sources: str = Field(description="Full direct text chunk from the context used to answer the question")
		regex: list[str] = Field(description="List of valid Python regex patterns. Each pattern must use proper regex syntax with anchors (^ and $), escaped special chars (\\d not d), and must match the exact TIN format described in the document. One pattern per TIN variation.")
		country: str = Field(description="What is the country name? Reply with only the country name, nothing else. Capitalize only the first letters")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Text chunks
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ```
# Splitting the document based on a given size and overlap size
# ```
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
											chunk_overlap=50,
											length_function=len, # how we count the characters
											separators=["\n\n", 	# page break
															"\n",	# line break
															" "])

evaluator = load_evaluator(evaluator="embedding_distance",
							embeddings=get_embedding)

# ```
# Loading pages and splitting them to small chunks
# ```
def chunk_from_file(filepath):
	loader = PyPDFLoader(filepath)
	pages = loader.load()
	chunks = text_splitter.split_documents(pages)
	return chunks

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Retriever "machine"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ```
# Chroma datbase
# Processing all the pages and creating a unique identifier for each chunk
# Creating vectors (quantified semantic meaning) with the llm embedding function
# ```
def create_vector_storage(chunks, embedding_function):
	# Making sure there are no duplicates
	# Create a list of unique ids for each document based on the content
	ids = []
	for doc in chunks:		# doc is a temporary variable for iteration
		doc_page_content = doc.page_content				# doc is a LangChain document object containing plain text and metadata, so we need to access plain text
		seed = uuid.NAMESPACE_DNS						# seed for the mathematical formula (called SHA-1 hashing). This one is the conventional default
		myUniqueID = uuid.uuid5(seed, doc_page_content)	# uuid5 is deterministic: same chink always creates the same id
		ids.append(str(myUniqueID))
	# the above is identical to this "list comprehension"
	#		ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]

	unique_ids = set()
		# an emtpy container. set is a list without duplicates
		# this will store all the uniques ids
	unique_chunks = []
		# this will store all the uniques chunks

	# Ensure that only unique docs with unique ids are kept
	for chunk, id in zip(chunks, ids):		# zip pairs the chunks with the ids.  
		if id not in unique_ids:       		# loops and adds if we dont have it yet
			unique_ids.add(id)
			unique_chunks.append(chunk) 

	# Creating the chroma database
	vector_storage = Chroma.from_documents(documents = unique_chunks,
										ids = list(unique_ids),
										embedding = embedding_function)
	return vector_storage

def create_retriever(chunks):
	vector_storage = create_vector_storage(chunks=chunks,
									embedding_function=get_embedding)
	retriever = vector_storage.as_retriever(search_type="similarity") 	#uses cos(distance) to determine similarity
	return retriever

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LLM answer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def format_docs(docs):
	return "\n\n---\n\n".join([doc.page_content for doc in docs])

def ask_llm_w_context(question, retriever):
	relevant_chunks = retriever.invoke(question)
	promt = prompt_template.format(context=format_docs(relevant_chunks),
								question=question)
	with_structured = llm.with_structured_output(structuredAnswer, strict=True)
	answer = with_structured.invoke(promt)
	return answer

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Processing the new documents
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def processing_new_document(filepath):
	chunks = chunk_from_file(filepath)
	retriever = create_retriever(chunks)
	answer = ask_llm_w_context("What is the TIN structure for this country? Identify the country name also", retriever)
	return answer

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Adding new data to the storage
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def add_or_overwrite(new_data: structuredAnswer, regex_storage, regex_filepath):
	country = new_data.country
	regex_storage[country] = new_data.model_dump()
	with open(regex_filepath, "w") as file:	# open to write
		json.dump(regex_storage, file, indent=4, sort_keys=True)