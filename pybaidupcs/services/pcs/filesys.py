#encoding:utf8
import json
from clients import BaiduPCS, BaiduPCSException
from services.pcs import restore_path, safe_path

__all__ = [
	"delete",
	"copy",
	"fileinfo",
	"find",
	"listfiles",
	"mkdir",
	"move"
]

def delete(paths, force=False):
	"""
	delete files or directories, force:ignore nonexistent files
	"""
	paths = paths if isinstance(paths, list) else [paths]
	params = [{"path": restore_path(path)} for path in paths]
	client = BaiduPCS()
	try:
		return client.file.post(method="delete", param=json.dumps({"list":params}))
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

def find(keyword, path='/'):
	"""
	find files
	"""
	client = BaiduPCS()
	resp = client.file.get(method="search", path=restore_path(path), re=1, 
		wd=keyword)
	res = resp["list"]
	for f in res:
		f["path"] = safe_path(f["path"])
	return res

def listfiles(path):
	"""
	list files and directories
	"""
	client = BaiduPCS()
	resp = client.file.get(method="list", path=restore_path(path))
	res = resp["list"]
	for f in res:
		f["path"] = safe_path(f["path"])
	return res

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