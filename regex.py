# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    regex.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/31 14:09:50 by zpalotas          #+#    #+#              #
#    Updated: 2026/05/31 18:28:02 by zpalotas         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python
# coding: utf-8

import re

def find_matching_country(tin, storage):
	country_match = set()
	for country, details in storage.items():
		for regex in details["regex"]:			#some countries have more than one possible tin structure
			try:
				if re.fullmatch(regex, tin):		# .match only checks beginning trailing chars after chek is ignored
					country_match.add(country)
			except re.error:
				print(f"Invalid regex for {country}: {regex}")
	return country_match