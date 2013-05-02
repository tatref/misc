#!/usr/bin/env python
#-*- coding:utf-8 -*-

import socket
import struct

if __name__ == '__main__':
	host = "vortex.labs.overthewire.org"
	port = 5842

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	numbers = ""
	while len(numbers) != 16:
		numbers += s.recv(1024)

	total = sum(struct.unpack("<IIII", numbers))
	total = struct.pack("<q", total)	# sometimes it does not fit in unsigned int
	s.sendall(total)

	out = s.recv(1024)
	print out
