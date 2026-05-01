# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    data_extraction.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/05 20:01:51 by zpalotas          #+#    #+#              #
#    Updated: 2026/05/01 20:13:17 by zpalotas         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python
# coding: utf-8

import os
	# interact with your operating system (e.g. read env variables)
from dotenv import load_dotenv
	# reads your API key from a .env file
from IPython.display import display
	# dosplays tables in a nice way

# MY FUNCTIONS
from processing_files	import processing_new_document
from check_file_update	import is_already_processed, mark_as_processed

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Loading the documents
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
hash_store = "processed_files.json"
pdf_directory = os.fsdecode("data/TIN_description_pdfs/")
for file in os.listdir(pdf_directory):
	filepath = pdf_directory + file
	basename = os.path.basename(filepath)
	# ```
	# Checking if the file was already proccessed or not
	# Run processing (and calling LLM) only if the file is new 
	# ```
	print("Processing: ", basename)
	is_already_done, file_hash, processed = is_already_processed(filepath, hash_store)

	if is_already_done:
		print("✅ Already processed, loading from storage")
		print(file_hash)
	else:
		print("New document, processing...")
		processing_new_document(filepath)
		mark_as_processed(filepath, file_hash, processed, hash_store)
		print("✅ Processing done")