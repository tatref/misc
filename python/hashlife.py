#!/usr/bin/env python
#-*-coding:utf-8 -*-

from __future__ import print_function, division
import math

import wx

class Node(object):
	@staticmethod
	def newNode(raw_data):
		s = len(raw_data)
		if False:
			raise Exception("Array must be n**2 × n**2")
		else:
			return Node(raw_data)

	def __init__(self, raw_data):
		"""
			depth : starts at 0
			raw_data : bidimentional squared array
		"""
		self.size = len(raw_data)
		if self.size == 4:
			# End of recursion
			pass
		else:
			# Recursion
			pass
			
	def __str__(self):
		return ""

if __name__ == '__main__':
	raw_data = [[0,0,0,0],
				[0,0,0,0],
				[0,0,0,0],
				[0,0,0,0]]

	node = Node.newNode(raw_data)
	print(node)

