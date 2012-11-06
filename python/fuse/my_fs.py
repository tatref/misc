#!/usr/bin/env python

#	Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#	This program can be distributed under the terms of the GNU LGPL.
#	See the file COPYING.
#

import os, stat, errno
# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
	import _find_fuse_parts
except ImportError:
	pass
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
	raise RuntimeError, \
		"your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

hello_path = '/hello'
hello_str = 'Hello World!\n'

#class MyStat(fuse.Stat):
#	def __init__(self):
#		self.st_mode = 0
#		self.st_ino = 0
#		self.st_dev = 0
#		self.st_nlink = 0
#		self.st_uid = 0
#		self.st_gid = 0
#		self.st_size = 0
#		self.st_atime = 0
#		self.st_mtime = 0
#		self.st_ctime = 0

class HelloFS(Fuse):
	def __init__(self, *args, **kwargs):
		super(HelloFS, self).__init__()
		
		if not 'target' in kwargs:
			raise Exception("Provide target")
		if not 'cache_dir' in kwargs:
			raise Exception("Provide cache_dir")

		self.target = kwargs['target']
		self.cache_dir = kwargs['cache_dir']

		"""
			Cache for stat sys call (owner, mtime...)
		"""
		self.stat_cache = {}

	def getattr(self, path):
		# get value from cache if possible
		if path in self.stat_cache:
			st = self.stat_cache[path]
		else:
			st = os.stat(self.target + path)

			# add value to cache
			self.stat_cache[path] = st

		return st

	def readdir(self, path, offset):
		# try to get value from cache
		if os.path.exists(self.cache_dir + path) and path != "/":
			dirs = os.listdir(self.cache_dir + path)
		else:
			dirs = os.listdir(self.target + path)

			# add to cache
			for r in dirs:
				if os.path.isdir(r):
					os.mkdir(self.cache_dir + r)
				elif os.path.isfile(r):
					#TODO
					# Create file (name)
					# copy content
					pass

		for r in  dirs:
			yield fuse.Direntry(r)

	def open(self, path, flags):
		if path != hello_path:
			return -errno.ENOENT
		accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
		if (flags & accmode) != os.O_RDONLY:
			return -errno.EACCES

	def read(self, path, size, offset):
		if path != hello_path:
			return -errno.ENOENT
		slen = len(hello_str)
		if offset < slen:
			if offset + size > slen:
				size = slen - offset
			buf = hello_str[offset:offset+size]
		else:
			buf = ''
		return buf

	def chmod ( self, path, mode ):
		print '*** chmod', path, oct(mode)
		return -errno.ENOSYS

def main():
	usage="""
Userspace hello example

""" + Fuse.fusage
	server = HelloFS(
		version="%prog " + fuse.__version__,
		usage=usage,
		dash_s_do='setsingle',
		target = "/mnt/music",
		cache_dir = "/home/yann/tmp/fuse/cache"
		)

	server.parse(errex=1)
	server.main()

if __name__ == '__main__':
	main()
