# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    processing_files.py                                :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/05 19:58:55 by zpalotas          #+#    #+#              #
#    Updated: 2026/04/05 23:39:37 by zpalotas         ###   ########.fr        #
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
from langchain_core.runnables import RunnablePassthrough
	# plumbing - connects steps of your pipeline together
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
import pandas as pd
	# spreadsheet-like data manipulation
from IPython.display import display
	# dosplays tables in a nice way

# MY FUNCTIONS
from llm_config			import llm, get_embedding
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Processing the new documents
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def processing_new_document(filepath): #TODO move reused funcs outside
	# ```
	# Loading
	# ```
	loader = PyPDFLoader(filepath)
	pages = loader.load()

	# ```
	# Splitting
	# ```
	text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
												chunk_overlap=50,
												length_function=len, # how we count the characters
												separators=["\n\n", 	# page break
																"\n",	# line break
																" "])
	chunks = text_splitter.split_documents(pages)

	# ```
	# ```

	evaluator = load_evaluator(evaluator="embedding_distance",
							embeddings=get_embedding)



	# ```
	# Chroma datbase
	# ```
	def create_vector_storage(chunks, embedding_function, storage_path):
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
											embedding = embedding_function,
											persist_directory = storage_path)
		#vector_storage.persist() #does it automatically
		return vector_storage


	vector_storage = create_vector_storage(chunks=chunks,
										embedding_function=get_embedding,
										storage_path="vector_storage_chroma")
	#load vector_storage
	vector_storage = Chroma(persist_directory="vector_storage_chroma", embedding_function=get_embedding)


	retriever = vector_storage.as_retriever(search_type="similarity") 	#uses cos(distance) to determine similarity
	# similarity:	Finds the chunks whose vectors are closest to the query vector. Pure distance measurement.
	# mmr: 			Maximum Marginal Relevance: If two chunks are very similar to each other, it picks one and skips the other in favour of something slightly less relevant but more different.
	#				Useful when your PDF has repetitive content 
	# similarity_score_threshold: Same as similarity but lets you set a minimum score — chunks below that threshold get rejected entirely even if they're the closest available.
	#				Useful when you'd rather return nothing than return something irrelevant.
	# extra parameter:  how many chunks get returned:
	# search_kwargs={"k": 5}  # default is 4

	relevant_chunks = retriever.invoke("What is the TIN structure for this country?")

	#Prompt instructions
	PROMPT_TEMPLATE = """
	Use the following pieces of retieved information only to answer the question
	If you don't know the answer, say "I don't know", Don't make up anything.
	If there is ambiguity, say "I am uncertain"API_KEY

	{context}

	Answer based on the above context: {question}
	"""


	formatting = "\n\n---\n\n".join([doc.page_content for doc in relevant_chunks])

	prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
	promt = prompt_template.format(context=formatting,
								question="How are the TINs structured for this country?")
	llm.invoke(promt)

	#pydantic is a data validation lib for python. to specify the stucture of the answer

	class structuredAnswer(BaseModel):
		answer: str = Field(description="Concise answer to the question")
		sources: str = Field(description="Full direct text chunk from the context used to answer the question")
		regex: str = Field(description="Create a regex that will be processed and compared to real life TINs, and need to be reliably determined if the TIN fufills the regex")


	def format_docs(docs):
		return "\n\n---\n\n".join([doc.page_content for doc in docs])

	rag_chain = (
				{"context": retriever | format_docs, "question":RunnablePassthrough()}
				| prompt_template
				| llm.with_structured_output(structuredAnswer, strict=True)
	)
	final_answer = rag_chain.invoke("How are the TINs structured for this country?")


	df = pd.DataFrame([final_answer.model_dump()])
	#same as
		#df = pd.DataFrame({
		#    "answer": [final_answer.answer],
		#    "sources": [final_answer.sources],
		#    "regex": [final_answer.regex]
		#})
	display(df)


