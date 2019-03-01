"""
	This file includes some common functions.
	
	functions:
		my_random_func, return a random list based three parameters.

"""

import random


def my_random_func(length, min_value, max_value):
	"""
	Given a range and the list length, return a no duplicates list.
	:param int length: list length.
	:param int min_value: min of range.
	:param int max_value: max of range.
	:return list: random list.
	"""
	random_list = []
	count = 0
	while count < length:
		random_value = random.randint(min_value, max_value)
		if random_value not in random_list:
			random_list.append(random_value)
			count = count + 1
	
	return random_list
