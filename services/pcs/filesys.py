#encoding:utf8
from clients import BaiduPCS, BaiduPCSException
from services.pcs import restore_path

__all__ = [
	"delete",
	"copy",
	"fileinfo",
	"listfiles",
	"mkdir",
	"move"
]

def delete(path, force=False):
	"""
	delete file or directory, force:ignore nonexistent files
	"""
	client = BaiduPCS()
	try:
		return client.file.post(method="delete", path=restore_path(path))
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
	return client.file.post(**{"method":"copy", 
		"from":restore_path(from_), "to":restore_path(to)})

def fileinfo(path):
	"""
	get file metainfo
	"""
	client = BaiduPCS()
	resp = client.file.get(method="meta", path=restore_path(path))
	return resp["list"][0]

def listfiles(path):
	"""
	list files and directories
	"""
	client = BaiduPCS()
	resp = client.file.get(method="list", path=restore_path(path))
	return resp["list"]

def mkdir(path):
	"""
	make a directory
	"""
	client = BaiduPCS()
	return client.file.post(method="mkdir", path=restore_path(path))

def move(from_, to, force=False):
	"""
	move file or directory, force:remove existing destination file
	"""
	if force:
		delete(to, True)
	client = BaiduPCS()
	return client.file.post(**{"method":"move",
		"from":restore_path(from_), "to":restore_path(to)})