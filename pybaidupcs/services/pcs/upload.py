#encoding:utf8
from collections import defaultdict
import json
from math import ceil
from hashlib import md5
import os
from clients import File, BaiduPCS, BaiduPCSException
from common import CloseableClass
from config import config
from services.pcs import hashfile, restore_path, temp_file

__all__ = [
	"check_rapidupload",
	"rapidupload_info",
	"Upload"
]

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
			resp = client.file.post(**kwargs)
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
			res["c_md5"], res["s_md5"] = hashfile(f)
	return res

def _logger(func):
	"""
	log upload
	"""
	from functools import wraps
	@wraps(func)
	def decorated_func(*args, **kwargs):
		import logging
		logging.info("upload begin")
		try:
			resp = func(*args, **kwargs)
		except Exception as e:
			logging.error("UNEXPECT EXIT! {error}".format(error=e))
			raise e
		logging.info("upload complete")
		return resp

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
		self.md5s = []
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
			# open file and read
			self._prepare()
			# judge upload method
			if self.filesize > config.UPLOADPIECE:
				self._multiupload()
				return check_rapidupload(**info)
			else:
				return self._singleupload()

	def _prepare(self):
		"""
		prepare before upload
		"""
		self.filesize = os.stat(self.localpath).st_size
		self.uploadsize = 0
		self.f = open(self.localpath, "rb")

	def close(self):
		"""
		close file
		"""
		if self.f:
			self.f.close()

	def _singleupload(self, ondup=None):
		"""
		upload file direct
		ondup = overwrite or newcopy
		"""
		return self.__upload(self.f.read(), self.uploadpath, ondup)

	def _multiupload(self, ondup=None):
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
		return client.file.post(**kwargs)

	def __upload_tempfile(self, content):
		"""
		upload temp files
		"""
		file = File("tmp", content)
		client = BaiduPCS()
		return client.file.post(method="upload", type="tmpfile", file=file)

	def __getslice(self):
		"""
		yield a piece of file
		return bytes, md5 of slice, md5 of first 256kb
		"""
		content = self.f.read(config.UPLOADPIECE)
		while content:
			yield content, md5(content).hexdigest(), md5(content[:256*1024]).hexdigest()
			content = self.f.read(config.UPLOADPIECE)

	def __add_md5_slice(self, content, slice_md5):
		"""
		add md5 slices into dict for merge file
		"""
		# if temp list is full 
		if len(self.tmp_md5s) == config.UPLOADPIECES:
			self.__clean_temp_md5s()
		self.tmp_md5sum.update(content)
		self.tmp_md5s.append(slice_md5)

	def __clean_temp_md5s(self):
		"""
		flush temp md5s cache
		"""
		md5_tuple = (self.tmp_md5s[0], []) if len(self.tmp_md5s) == 1 \
			else (self.tmp_md5sum.hexdigest(), self.tmp_md5s)
		self.md5s.append(md5_tuple)
		self.tmp_md5sum = md5()
		self.tmp_md5s = []

	def __yield_md5s(self):
		"""
		yield a slice of md5s for combine
		"""
		for small_pieces_sum, small_pieces in self.md5s:
			if small_pieces:
				yield small_pieces
		big_piece = list(map(lambda kv: kv[0], self.md5s))
		if len(big_piece) > 1:
			yield big_piece

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
		return client.file.post(method="createsuperfile", 
			path=restore_path(uploadpath), param=json.dumps({"block_list": list(md5s)}))