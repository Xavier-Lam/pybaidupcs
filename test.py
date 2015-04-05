#encoding:utf8
from hashlib import md5
from config import PIECE
from clients import BaiduPCS, BaiduPCSException
from services.pcsservice import restore_path
import time

def upload(localpath, uploadpath):
	for slice, p2, p3 in __getslice(localpath):
		check_rapidupload(len(slice), p2, p3)

def __getslice(localpath):
	"""
	yield a piece of file
	return bytes, md5 of slice
	"""
	with open(localpath, "rb") as f:
		content = f.read(PIECE)
		while content:
			yield content, md5(content).hexdigest(), md5(content[:256*1024]).hexdigest()
			content = f.read(PIECE)

def check_rapidupload(p1, p2, p3):
	"""
	judge whether a file can upload rapidly
	"""
	info = {}
	info["content-length"] = p1
	info["content-md5"] = p2
	info["slice-md5"] = p3

	# minimun of content-length is 256KB
	if info["content-length"] > 256*1024:
		client = BaiduPCS()
		# return file's md5 if can be rapidupload
		try:
			resp = client.pcs.file.post(method="rapidupload", 
				path=restore_path("/tmpfile/" + str(time.time())), **info)
			print("successed")
			return resp["md5"]
		except BaiduPCSException as e:
			# if not found return empty string
			print("failed")
			if not e.status == 404:
				raise e

if __name__ == "__main__":
	upload("f:\\wwp.iso", "testrapid")