#encoding:utf8
from collections import defaultdict, OrderedDict
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
	return path.replace('\\', '/').replace("//", '/')\
		.replace(config.PATHPREFIX, "", 1)

class temp_file:
	"""
	generate a temp file path and delete file when exit
	"""
	def __enter__(self):
		path = config.TEMPFILEFOLDER + "/__tmp_" + str(time.time()).replace('.', '_')
		self.__path = path
		return self.__path

	def __exit__(self, type, value, traceback):
		try:
			delete(self.__path)
		except:
			pass

def delete(path, force=False):
	"""
	delete file or directory, force:ignore nonexistent files
	"""
	client = BaiduPCS()
	try:
		return client.pcs.file.post(method="delete", path=restore_path(path))
	except BaiduPCSException as e:
		if not force or e.status != 404:
			raise e

def copy(from_, to, force=False):
	"""
	copy  file or directory, force:remove existing destination file
	"""
	if force:
		delete(to, True)
	client = BaiduPCS()
	return client.pcs.file.post(**{"method":"copy", 
		"from":restore_path(from_), "to":restore_path(to)})

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

def move(from_, to, force=False):
	"""
	move file or directory, force:remove existing destination file
	"""
	if force:
		delete(to, True)
	client = BaiduPCS()
	return client.pcs.file.post(**{"method":"move",
		"from":restore_path(from_), "to":restore_path(to)})

def check_rapidupload(c_length, c_md5, s_md5, uploadpath, ondup=None):
	"""
	judge whether a file can upload rapidly
		c_length: content length
		c_md5: content md5
		s_md5: slice md5
		ondup: overwrite or newcopy
	"""
	# minimun of content-length is 256KB
	if c_length > 256*1024:
		kwargs = {"content-length":c_length, "content-md5":c_md5, "slice-md5":s_md5,
			"method":"rapidupload", "path":restore_path(uploadpath)}
		if ondup:kwargs["ondup"] = ondup
		client = BaiduPCS()
		# return file's md5 if can be rapidupload
		try:
			resp = client.pcs.file.post(**kwargs)
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
	res = defaultdict(str)
	# open and hash file
	res["c_length"] = os.stat(localpath).st_size
	# minimun of content-length is 256KB
	if res["c_length"] > 256*1024:
		with open(localpath, "rb") as f:
			res["c_md5"], res["s_md5"] = __hashfile(f)
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

	def __call__(self, force=False, rapid=True):
		"""
		do upload
		"""
		# check rapid upload first
		info = rapidupload_info(self.localpath)
		info["uploadpath"] = self.uploadpath
		if force: info["ondup"] = "overwrite"
		if not rapid or not check_rapidupload(**info):
			self.filesize = os.stat(self.localpath).st_size
			self.uploadsize = 0
			# open file and read
			self.f = open(self.localpath, "rb")
			# judge upload method
			if self.filesize > config.PIECE:
				self.__multiupload()
				return check_rapidupload(**info)
			else:
				return self.__singleupload()

	def close(self):
		"""
		close file
		"""
		if self.f:
			self.f.close()

	def __singleupload(self, ondup=None):
		"""
		upload file direct
		ondup = overwrite or newcopy
		"""
		return self.__upload(self.f.read(), self.uploadpath, ondup)

	def __multiupload(self, ondup=None):
		"""
		split file into parts and upload
		ondup = overwrite or newcopy
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
		if ondup: kwargs["ondup"] = ondup
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
		return bytes, md5 of slice, md5 of first 256kb
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
		flush temp md5s cache
		"""
		if len(self.tmp_md5s) == 1:
			self.md5s[self.tmp_md5s[0]] == []
		else:
			self.md5s[self.tmp_md5sum.hexdigest()] = self.tmp_md5s
		self.tmp_md5sum = md5()
		self.tmp_md5s = []

	def __yield_md5s(self):
		"""
		yield a slice of md5s for combine
		"""
		for md5s in self.md5s.values():
			if md5s:
				yield md5s
		if len(self.md5s.keys()) > 1:
			yield self.md5s.keys()

	def __merge_file(self):
		"""
		merge file
		"""
		self.__clean_temp_md5s()
		for md5s in self.__yield_md5s():
			with temp_file() as temppath:
				resp = self.__combine_files(md5s, temppath)
		return resp

	def __combine_files(self, md5s, uploadpath):
		"""
		combine file slices into 1
		"""
		client = BaiduPCS()
		return client.pcs.file.post(method="createsuperfile", 
			path=restore_path(uploadpath), param=json.dumps({"block_list": list(md5s)}))

def __hashfile(file, blocksize=4*1024*1024):
	"""
	3431825/generating-a-md5-checksum-of-a-file
	Omnifarious
	return content-md5, slice-md5
	"""
	md5obj = md5()
	# first slice check for rapid upload
	first_slice = buf = file.read(256*1024)
	while(len(buf)>0):
		md5obj.update(buf)
		buf = file.read(blocksize)
	return md5obj.hexdigest(), md5(first_slice).hexdigest()