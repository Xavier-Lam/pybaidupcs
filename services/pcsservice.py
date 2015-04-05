#encoding:utf8
from hashlib import md5
import json
from math import ceil
import os
import time
try:
	from urllib.parse import quote
except ImportError:
	from urllib import quote
from clients import *
from config import PIECE

__isfile = lambda content:isinstance(content, str) and os.path.isfile(content)

def safe_path(path, encode=True):
	"""
	add path prefix and replace '/' with %2F
	"""
	from config import PATHPREFIX
	# replace \\ with /
	path = path.replace('\\', '/')
	# if path start with / then delete it
	path = path.lstrip('/')
	# add prefix
	path = PATHPREFIX + '/' + path
	return quote(path, "") if encode else path

def delete(path):
	"""
	delete file or directory
	"""
	client = BaiduPCS()
	return client.pcs.file.post(method="delete", path=safe_path(path, False))

def fileinfo(path):
	"""
	get file metainfo
	"""
	client = BaiduPCS()
	resp = client.pcs.file.get(method="meta", path=safe_path(path))
	return resp["list"][0]

class temp_file:
	"""
	generate a temp file path delete file when exit
	"""
	def __enter__(self):
		path = "/__tmp/__tmp_" + str(time.time()).replace('.', '_')
		self.__path = path
		return self.__path

	def __exit__(self, type, value, traceback):
		try:
			delete(self.__path)
		except:
			pass

def listfiles(path):
	"""
	list files and directories
	"""
	client = BaiduPCS()
	resp = client.pcs.file.get(method="list", path=safe_path(path))
	return resp["list"]

def mkdir(path):
	"""
	make a directory
	"""
	client = BaiduPCS()
	return client.pcs.file.post(method="mkdir", path=safe_path(path, False))

def upload(localpath, uploadpath, progress_recall=None):
	"""
	judge upload method
	"""
	# check for rapid upload
	if check_rapidupload(localpath, uploadpath):
		return
	filesize = os.stat(localpath).st_size
	if filesize > PIECE:
		md5s = multiupload(localpath, uploadpath, filesize, progress_recall)
		return combine_files(md5s, uploadpath)
	else:
		return __upload(localpath, uploadpath)

def check_rapidupload(localpath, uploadpath):
	"""
	judge whether a file can upload rapidly
	"""
	info = rapidupload_info(content, c_length)
	# minimun of content-length is 256KB
	if info["content-length"] > 256*1024:
		client = BaiduPCS()
		# return file's md5 if can be rapidupload
		try:
			resp = client.pcs.file.post(method="rapidupload", 
				path=safe_path(uploadpath, False), **info)
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

class Upload:
	"""
	upload files
	"""
	def __init__(self, localpath, uploadpath):
		self.localpath = localpath
		self.uploadpath = uploadpath
		self.progress_callback = None

	def __call__(self):
		"""
		do upload
		"""
		# check rapid upload first
		if not check_rapidupload(self.localpath, self.uploadpath):
			pass

def __upload(content, uploadpath):
	"""
	upload file direct
	content is local file path or loaded bytes
	"""
	client = BaiduPCS()
	if __isfile(content):
		with open(content, "rb") as f:
			file = File(os.path.split(content)[1], f.read())
	else:
		file = File("tmp", content)
	resp = client.pcs.file.post(method="upload", 
		path=safe_path(uploadpath), file=file)
	return resp

def multiupload(localpath, uploadpath, filesize, progress_recall=None):
	"""
	split file into path and upload
	"""
	# split into pieces
	pieces = ceil(filesize/PIECE)
	md5s = []
	with open(localpath, "rb") as f:
		for i in range(pieces):	
			# return to main and yield some information
			if progress_recall:progress_recall(i/pieces*100)
			content = f.read(PIECE)
			md5s.append(md5(content).hexdigest())
			# check rapidupload
			with temp_file() as temppath:
				if not check_rapidupload(content, temppath):
					__upload(content, temppath)
	return md5s

def combine_files(md5s, uploadpath):
	"""
	combine multi upload files
	"""
	client = BaiduPCS()
	# max acceptable md5 list length is 1024
	# if length of md5s greater than 1024
	# combine them first
	while len(md5s) > 1024:
		with temp_file() as temppath:
			new_md5 = combine_files(md5s[:1024])["md5"]
			del(md5s[:1024])
			md5s.insert(0, new_md5)
	resp = client.pcs.file.post(method="createsuperfile", path=safe_path(uploadpath, False), 
		param=json.dumps({"block_list": md5s}))
	return resp

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