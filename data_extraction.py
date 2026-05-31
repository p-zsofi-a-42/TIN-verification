# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    data_extraction.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/05 20:01:51 by zpalotas          #+#    #+#              #
#    Updated: 2026/05/31 13:53:02 by zpalotas         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python3
# coding: utf-8

import os
	# interact with your operating system (e.g. read env variables)
from dotenv import load_dotenv
	# reads your API key from a .env file
from IPython.display import display
	# dosplays tables in a nice way
import json
	# reads and writes JSON files (key-value storage)

# MY FUNCTIONS
from processing_files	import processing_new_document, structuredAnswer, add_or_overwrite
from check_file_update	import check_process_status, mark_as_processed

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Loading processed docs regexes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
regex_filepath = "regex_storage.json"
if os.path.exists(regex_filepath):
	with open(regex_filepath, "r") as file:
		regex_storage = json.load(file)
else:
	regex_storage = {}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Loading the documents
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
hash_store = "./processed_files.json"
pdf_directory = os.fsdecode("data/TIN_description_pdfs/")
for file in os.listdir(pdf_directory):
	filepath = pdf_directory + file
	basename = os.path.basename(filepath)
	# ```
	# Checking if the file was already proccessed or not
	# Run processing (and calling LLM) only if the file is new 
	# ```
	print("Processing: ", basename)
	is_already_processed, file_hash, processed_documents = check_process_status(filepath, hash_store)

	if not is_already_processed:
		print("✅ Already processed, loading from storage")
		print(file_hash)
	else:
		print("New document, processing...")
		new_data = processing_new_document(filepath)
		mark_as_processed(filepath, file_hash, processed_documents, hash_store)
		print("✅ Processing done")
		add_or_overwrite(new_data, regex_storage, regex_filepath)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Validating TIN
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TIN_input = input("\nEnter a TIN: ")

import re

def find_matching_country(tin, df):
    for index, row in df.iterrows():
        pattern = row["regex"]
        if re.match(pattern, tin):
            return row["answer"]  # or whatever column has the country name
    return "No match found"