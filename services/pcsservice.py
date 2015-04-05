#encoding:utf8
from collections import OrderedDict
from hashlib import md5
import json
from math import ceil
import os
import time
from clients import *
from common import CloseableClass
from config import config

def restore_path(path):
	"""
	add path prefix 
	"""
	# replace \\ with /
	path = path.replace('\\', '/')
	# if path start with / then delete it
	path = path.lstrip('/')
	# add prefix
	return config.PATHPREFIX + '/' + path

def safe_path(path):
	"""
	delete path prefix and replace '\\' with ""
	"""
	return path.replace('\\', "").replace(config.PATHPREFIX, "", 1)

class temp_file:
	"""
	generate a temp file path delete file when exit
	"""
	def __enter__(self):
		path = config.TEMPFOLDER + "/__tmp_" + str(time.time()).replace('.', '_')
		self.__path = path
		return self.__path

	def __exit__(self, type, value, traceback):
		try:
			delete(self.__path)
		except:
			pass

def copy(from_, to):
	"""
	copy  file or directory
	"""
	client = BaiduPCS()
	return client.pcs.file.post(**{"method":"copy", 
		"from":restore_path(from_), "to":restore_path(to)})

def delete(path):
	"""
	delete file or directory
	"""
	client = BaiduPCS()
	return client.pcs.file.post(method="delete", path=restore_path(path))

def fileinfo(path):
	"""
	get file metainfo
	"""
	client = BaiduPCS()
	resp = client.pcs.file.get(method="meta", path=restore_path(path))
	return resp["list"][0]

def listfiles(path):
	"""
	list files and directories
	"""
	client = BaiduPCS()
	resp = client.pcs.file.get(method="list", path=restore_path(path))
	return resp["list"]

def mkdir(path):
	"""
	make a directory
	"""
	client = BaiduPCS()
	return client.pcs.file.post(method="mkdir", path=restore_path(path))

def move(from_, to):
	"""
	move file or directory
	"""
	client = BaiduPCS()
	return client.pcs.file.post(**{"method":"move",
		"from":restore_path(from_), "to":restore_path(to)})

def check_rapidupload(c_length, c_md5, s_md5, uploadpath):
	"""
	judge whether a file can upload rapidly
		c_length: content length
		c_md5: content md5
		s_md5: slice md5
	"""
	# minimun of content-length is 256KB
	if c_length > 256*1024:
		info = {}
		info["content-length"] = c_length
		info["content-md5"] = c_md5
		info["slice-md5"] = s_md5
		client = BaiduPCS()
		# return file's md5 if can be rapidupload
		try:
			resp = client.pcs.file.post(method="rapidupload", 
				path=restore_path(uploadpath), **info)
			return resp["md5"]
		except BaiduPCSException as e:
			# if not found return empty string
			if not e.status == 404:
				raise e

def rapidupload_info(localpath):
	"""
	generate rapidupload needed info 
	return content-length, content-md5, slice-md5 as a dict
	"""
	res = {}
	# open and hash file
	res["content-length"] = os.stat(localpath).st_size
	with open(localpath, "rb") as f:
		res["slice-md5"], res["content-md5"] = __hashfile(f)
	return res

class Upload(CloseableClass):
	"""
	upload files
	"""
	def __init__(self, localpath, uploadpath):
		self.localpath = localpath
		self.uploadpath = uploadpath
		# progress bar callback
		self.progress_callback = None
		# opened file
		self.f = None
		# md5 list of slices
		self.md5s = OrderedDict()
		# temp md5 list(yet not check sum)
		self.tmp_md5s = []
		# temp sum of tmp_md5s
		self.tmp_md5sum = md5()

	def __call__(self, force=False):
		"""
		do upload
		"""
		# check rapid upload first
		info = rapidupload_info(self.localpath)
		if force or not check_rapidupload(info["content-length"], 
			info["content-md5"], info["slice-md5"], self.uploadpath):
			self.filesize = os.stat(self.localpath).st_size
			self.uploadsize = 0
			# open file and read
			self.f = open(self.localpath, "rb")
			# judge upload method
			if self.filesize > config.PIECE:
				return self.__multiupload()
			else:
				return self.__singleupload()

	def close(self):
		"""
		close file
		"""
		if self.f:
			self.f.close()

	def __singleupload(self):
		"""
		upload file direct
		"""
		return self.__upload(self.f.read(), self.uploadpath)

	def __multiupload(self):
		"""
		split file into parts and upload
		"""
		for content, c_md5, s_md5 in self.__getslice():
			# show upload stat
			if self.progress_callback:
				self.progress_callback(self.uploadsize/self.filesize*100)
			c_length = len(content)
			# try rapid upload
			with temp_file() as temppath:
				if not check_rapidupload(c_length, c_md5, s_md5, temppath):
					self.__upload_tempfile(content)
			# add this piece of md5 into dict(md5 dict use in merge file)
			self.__add_md5_slice(content, c_md5)
			self.uploadsize = self.uploadsize + c_length
		# return upload result
		return self.__merge_file()

	def __upload(self, content, uploadpath, ondup=None):
		"""
		upload file direct
		ondup = overwrite or newcopy
		content is local file path or loaded bytes
		"""
		file = File(os.path.split(uploadpath)[1], content)
		client = BaiduPCS()
		kwargs = dict(method="upload", path=restore_path(uploadpath), file=file)
		if ondup:
			kwargs["ondup"] = ondup
		return client.pcs.file.post(**kwargs)

	def __upload_tempfile(self, content):
		"""
		upload temp files
		"""
		file = File("tmp", content)
		client = BaiduPCS()
		return client.pcs.file.post(method="upload", type="tmpfile", file=file)

	def __getslice(self):
		"""
		yield a piece of file
		return bytes, md5 of slice
		"""
		content = self.f.read(config.PIECE)
		while content:
			yield content, md5(content).hexdigest(), md5(content[:256*1024]).hexdigest()
			content = self.f.read(config.PIECE)

	def __add_md5_slice(self, content, slice_md5):
		"""
		add md5 slices into dict for merge file
		"""
		# if temp list is full 
		if len(self.tmp_md5s) == config.PIECES:
			self.__clean_temp_md5s()
		self.tmp_md5sum.update(content)
		self.tmp_md5s.append(slice_md5)

	def __clean_temp_md5s(self):
		"""
		
		"""
		self.md5s[self.tmp_md5sum.hexdigest()] = self.tmp_md5s
		self.tmp_md5sum = md5()
		self.tmp_md5s = []

	def __merge_file(self):
		"""
		merge file
		"""
		self.__clean_temp_md5s()
		for v in self.md5s.values():
			with temp_file() as temppath:
				self.__combine_files(v, temppath)
		return self.__combine_files(self.md5s.keys(), self.uploadpath)

	def __combine_files(self, md5s, uploadpath):
		client = BaiduPCS()
		return client.pcs.file.post(method="createsuperfile", 
			path=restore_path(uploadpath), param=json.dumps({"block_list": list(md5s)}))

def __hashfile(file, blocksize=4*1024*1024):
	"""
	3431825/generating-a-md5-checksum-of-a-file
	Omnifarious
	return slice-md5, content-md5
	"""
	md5obj = md5()
	# first slice check for rapid upload
	first_slice = buf = file.read(256*1024)
	while(len(buf)>0):
		md5obj.update(buf)
		buf = file.read(blocksize)
	return md5(first_slice).hexdigest(), md5obj.hexdigest()