# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    llm_config.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/05 20:07:43 by zpalotas          #+#    #+#              #
#    Updated: 2026/04/09 16:08:21 by zpalotas         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python
# coding: utf-8

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
	# Gemini embeddings model and a chat model
import os
	# interact with your operating system (e.g. read env variables)
from dotenv import load_dotenv
	# reads your API key from a .env file

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Setting up the LLM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ```
# Reading env file
# ```
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

# ```
# Using Gemini's free version
# ```
llm = ChatGoogleGenerativeAI(
		model="gemini-2.5-flash-lite",
		google_api_key=API_KEY
		)

# ```
# Init Gemini embedding function
# ```
get_embedding = GoogleGenerativeAIEmbeddings(
			model="gemini-embedding-001", google_api_key=API_KEY
		)