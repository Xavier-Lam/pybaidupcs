#encoding:utf8
from hashlib import md5
import time
from config import config

__all__ = [
	"restore_path",
	"safe_path",
	"temp_file",
	"hashfile",
	"check_rapidupload",
	"Upload",
	"delete",
	"copy",
	"fileinfo",
	"find",
	"listfiles",
	"mkdir",
	"move",
	"Download",
	"request_piece"
]

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

class temp_file(object):
	"""
	generate a temp file path and delete file when exit
	"""
	def __init__(self):
		path = config.TEMPFILEFOLDER + "/__tmp_" + str(time.time()).replace('.', '_')
		self.path = path

	def __enter__(self):
		return self.path

	def __exit__(self, type, value, traceback):
		delete(self.path, True)

def hashfile(file, blocksize=4*1024*1024):
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

# def encode(path, type_="M3U8_320_240"):
# 	"""
# 	encode videos
# 	"""
# 	from clients import BaiduPCS
# 	client = BaiduPCS()
# 	req = client.pcs.file.get
# 	req.raw = True
# 	return req(path=restore_path(path), method="streaming", type=type_)

from services.pcs.filesys import *
from services.pcs.download import *
from services.pcs.upload import *