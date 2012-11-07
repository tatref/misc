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

import logging
import hashlib
import shutil

logger = logging.getLogger("my_fs")
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
f = logging.FileHandler("/home/yann/misc/python/fuse/my_fs.log")
f.setFormatter(formatter)
logger.addHandler(f)

# log all
logger.setLevel(logging.INFO)


if not hasattr(fuse, '__version__'):
	raise RuntimeError, \
		"your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

class HelloFS(Fuse):
	def __init__(self, *args, **kwargs):
		super(HelloFS, self).__init__()
		
		if not 'target' in kwargs:
			raise Exception("Provide target")
		if not 'cache_dir' in kwargs:
			raise Exception("Provide cache_dir")

		self.target = kwargs['target']
		self.cache_dir = kwargs['cache_dir']

		#init cache
		self.stat_cache = {}
		self.stat_cache["/"] = os.stat(self.target)

	def getattr(self, path):
		logger.info("getattr " + path)

		# get value and update cache
		st = os.stat(self.target + path)
		self.stat_cache[path] = st

		return st

	def readdir(self, path, offset):
		# is cache up-to-date ?
		subs = os.listdir(self.target + path)

		for r in subs:
			yield fuse.Direntry(r)

	def open(self, path, flags):
		return 0

	def read(self, path, size, offset):
		logger.info("read path=" + path + " size=" + str(size) + " offset=" + str(offset))

		cache_path = os.path.join(self.cache_dir, path[1:])
		target_path = os.path.join(self.target, path[1:])

		try:
			if os.stat(target_path).st_mtime > self.stat_cache[path].st_mtime:
				logger.info("new version of " + path + " available, removing old")
				# new version of file available !
				os.remove(cache_path)
		except:
			logger.warning("unable to get last modify time for " + path + ", falling back to cache")

		if os.path.exists(cache_path):
			logger.info("getting content of " + path + " from cache")
		else:
			logger.info("copying content of " + target_path + " to " + cache_path)
			
			d = self.cache_dir + "/" + "/".join(path.split("/")[1:-1])
			if not os.path.exists(d):
				os.mkdir(d)
				shutil.copyfile(target_path, cache_path)
			

		f = open(cache_path)
		f.seek(offset)
		out = f.read(size)
		f.close()

		return out
			

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
		cache_dir = "/home/yann/misc/python/fuse/cache"
		)

	server.parse(errex=1)
	server.main()

	


if __name__ == '__main__':
	main()
