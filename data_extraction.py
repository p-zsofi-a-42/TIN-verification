# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    data_extraction.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/05 20:01:51 by zpalotas          #+#    #+#              #
#    Updated: 2026/04/10 01:03:53 by zpalotas         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python
# coding: utf-8

import os
	# interact with your operating system (e.g. read env variables)
import hashlib
	# Python's built in hashing library
import json
	# reads and writes JSON files (key-value storage)
from dotenv import load_dotenv
	# reads your API key from a .env file
from IPython.display import display
	# dosplays tables in a nice way

# MY FUNCTIONS
from processing_files	import processing_new_document

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Loading the documents
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ```
# placeholder until we incorporate more than one
# ```
#filepath = "data/TIN_description_pdfs/austria-tin.pdf"
#filepath = "data/TIN_description_pdfs/brunei-darussalam-tin.pdf"
filepath = "data/TIN_description_pdfs/china-tin.pdf"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Checking hash of the documents
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ```
# The file which stores all the hashes
# ```
hash_store = "processed_files.json"

# ```
# Opening the file, reading it's bytes and producing a hash
# ```
def get_file_hash(filepath):							# opens in read binary mode (raw bytes instead of text bc pdf can get corroupted if read as text)
	with open(filepath, "rb") as doc:					# "with" closes file when done or crash
		hash_object = hashlib.md5(doc.read())			# hashlib.md5 is the same as uuid but uuid expects a string whereas this one wants raw bytes
		readable_hash_object = hash_object.hexdigest()	# converts the object to readable str
		return readable_hash_object

# ```
# Checks if the file has been processed already
# searches the json file
# returns the stored or (if not found) newly created hash 
# ```
def is_already_processed(filepath, hash_store):
	if os.path.exists(hash_store):					# check if my json file exist
		with open(hash_store, "r") as store_file:	# if exist open as "read only"
			processed = json.load(store_file)		# convert json to python readable object, and load the hashes that exist
	else:
		processed = {}								# if doesnt exist create instead of crashing

	file_hash = get_file_hash(filepath)				# call my func to get the unique hash if there was a prev version already

	return file_hash in processed.values(), file_hash, processed # processed.values(): True/False, has it been seen before

# ```
# Saving the new hash, rewriting or creating entry
# ```
def mark_as_processed(filepath, file_hash, processed, hash_store):
	processed[filepath] = file_hash				# rewrites or adds new entry: filename is key, hash is value
	with open(hash_store, "w") as store_file:	# open to write
		json.dump(processed, store_file)		# convert back to json. the reverse of json.load


# ```
# Checking if the file was already proccessed or not
# Run processing (and calling LLM) only if the file is new 
# ```
is_already_done, file_hash, processed = is_already_processed(filepath, hash_store)

if is_already_done:
	print("Already processed, loading from storage")
	print(file_hash)
else:
	print("New document, processing...")
	processing_new_document(filepath)
	mark_as_processed(filepath, file_hash, processed, hash_store)
	print("New document, processed...")