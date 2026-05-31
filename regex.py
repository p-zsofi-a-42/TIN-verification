# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    regex.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: zpalotas <zpalotas@42vienna.at>            +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/31 14:09:50 by zpalotas          #+#    #+#              #
#    Updated: 2026/05/31 17:11:20 by zpalotas         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python
# coding: utf-8

import re

def find_matching_country(tin, storage):
	country_match = set()
	for country, details in storage.items():
		pattern = details["regex"]
		if re.match(pattern, tin):
			country_match.add(country)
	return country_match