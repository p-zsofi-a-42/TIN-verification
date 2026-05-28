# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    check_file_update.py                               :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/01 20:13:26 by zpalotas          #+#    #+#              #
#    Updated: 2026/05/28 11:24:57 by zpalotas         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
	# interact with your operating system (e.g. read env variables)
import hashlib
	# Python's built in hashing library
import json
	# reads and writes JSON files (key-value storage)

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
	already_processed = file_hash in processed.values()  # Is? file_hash among the processed.values(): True/False, has it been seen before
	return already_processed, file_hash, processed

# ```
# Saving the new hash, rewriting or creating entry
# ```
def mark_as_processed(filepath, file_hash, processed, hash_store):
	processed[filepath] = file_hash				# rewrites or adds new entry: filename is key, hash is value
	with open(hash_store, "w") as store_file:	# open to write
		json.dump(processed, store_file, indent=4, sort_keys=True)		# convert back to json. the reverse of json.load
