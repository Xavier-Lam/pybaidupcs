#encoding:utf8
import os
from clients import BaiduPCS, BaiduPCSException
from common import ApplicationException, CloseableClass
from config import config
from services.pcs import fileinfo, restore_path

__all__ = ["Download", "request_piece"]

def request_piece(start_bytes, end_bytes, path):
	"""
	request a piece of file range starts from from_bytes and ends to_bytes
	"""
	client = BaiduPCS()
	req = client.file.get
	req.raw = True
	#add range in headers
	req.headers["Range"] = "bytes={start}-{end}"\
		.format(start=start_bytes, end=end_bytes)
	return req(method="download", path=restore_path(path))

def _logger(func):
	"""
	log download
	"""
	from functools import wraps
	@wraps(func)
	def decorated_func(*args, **kwargs):
		import logging
		logging.info("download begin")
		try:
			resp = func(*args, **kwargs)
		except Exception as e:
			logging.error("UNEXPECT EXIT! {error}".format(error=e))
			raise e
		logging.info("download complete")
		return resp

class Download(CloseableClass):
	"""
	Download file from baiduyun
	"""
	def __init__(self, downloadpath, localpath):
		self.downloadpath = downloadpath
		self.downloadfile_info = fileinfo(downloadpath)
		self.filesize = self.downloadfile_info["size"]
		self.localpath = localpath
		self.f = None
		self.start = 0
		# progress bar callback
		self.progress_callback = None

	def __call__(self, override=False, resume=False):
		"""
		start download file
		"""
		if os.path.isfile(self.localpath):
			if override:
				open(self.localpath, 'w').close()
			elif resume:
				# need add file validate!!!
				self.start = os.stat(self.localpath).st_size
			else:
				raise ApplicationException("local file already exists!")
		self.f = open(self.localpath, "ab")
		for piece in self.__get_piece():
			self.__store_file(piece)

	def __store_file(self, content):
		"""
		store got content into disk
		"""
		self.f.write(content)

	def __get_piece(self):
		"""
		get a piece of content from baiduyun
		"""
		for start_bytes in range(self.start, self.filesize, config.DOWNLOADPIECE):
			if self.progress_callback:
				self.progress_callback(start_bytes/self.filesize*100)
			yield request_piece(start_bytes, start_bytes+config.DOWNLOADPIECE-1, 
				self.downloadpath)

	def close(self):
		if self.f:
			self.f.close()