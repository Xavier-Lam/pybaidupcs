#encoding:utf8
from argparse import ArgumentParser
import os
from sys import argv, modules
import time
from clients import BaiduPCSException
from config import PATHPREFIX
from console.utils import bytes2human

current_module = modules[__name__]
usage_prefix = "python3 tsguploader.py"

parser = ArgumentParser(description="""TSGUploader

	This is a baiduyun toolkit writen in python use baidu rest api.
	Written by Xavier-Lam(13599838712@hotmail.com)
	""", usage=usage_prefix + " [COMMAND] [OPTION]... [ARGS]...")

# just for print description
parser.add_argument("info", help="show file infomation")
parser.add_argument("init", help="get user authorization")
parser.add_argument("ls", help="list directory contents")
parser.add_argument("mkdir", help="make directories")
parser.add_argument("rm", help="remove files or directories")
parser.add_argument("upload", help="upload files to baiduyun")

def __pcs_error_handler(func):
	"""
	handle pcs errors
	"""
	from functools import wraps
	@wraps(func)
	def decorated_func(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except BaiduPCSException as e:
			print("ERROR[{errorcode}]: {errormsg}\nStatus code:{status}"\
				.format(errorcode=e.error_code, errormsg=e.error_msg, status=e.status))
	return decorated_func

@__pcs_error_handler
def info():
	""" {help}
	{usageprefix} info FILEPATH
	WARNING: directory is under {pathprefix}"""
	parser = ArgumentParser(usage=info.__doc__)
	parser.add_argument("filepath", help="file or directory path")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcsservice import fileinfo
	print(fileinfo(args.filepath))

def init():
	""" {help}
	"""
	from services.openapiservice import apply_auth
	for i in apply_auth():
		print("please wait")

@__pcs_error_handler
def ls():
	""" {help}
	{usageprefix} ls DIRECTORY
	WARNING: directory is under {pathprefix}"""
	parser = ArgumentParser(usage=ls.__doc__)
	parser.add_argument("directory", help="directory name", default='/')
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcsservice import listfiles
	files = listfiles(args.directory)
	# format and print files
	for f in files:
		# transfer timestamp to time string
		mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(f["mtime"]))
		# if isdir then size display as <dir> else print size
		size = "<dir>" if f["isdir"] else bytes2human(f["size"])
		# erase path prefix
		filename = os.path.split(f["path"])[1]
		print("{mtime:20} {size:10} {filename}"\
			.format(mtime=mtime, size=size, filename=filename))

@__pcs_error_handler
def mkdir():
	""" {help}
	{usageprefix} mkdir DIRECTORY
	WARNING: directory is under {pathprefix}"""
	parser = ArgumentParser(usage=mkdir.__doc__)
	parser.add_argument("directory", help="directory name")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcsservice import mkdir as mkdirservice
	mkdirservice(args.directory)

@__pcs_error_handler
def rm():
	""" {help}
	{usageprefix} rm FILEPATH
	WARNING: directory is under {pathprefix}"""
	parser = ArgumentParser(usage=rm.__doc__)
	parser.add_argument("filepath", help="file or directory path")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcsservice import delete
	delete(args.filepath)

@__pcs_error_handler
def upload():
	""" {help}
	{usageprefix} upload LOCALPATH UPLOADPATH
	WARNING: directory is under {pathprefix}"""
	parser = ArgumentParser(usage=upload.__doc__)
	parser.add_argument("localpath", help="file path")
	parser.add_argument("uploadpath", help="upload path")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcsservice import upload as uploadservice
	uploadservice(args.localpath, args.uploadpath, lambda x: print("%.2f%%"%x))

def __call(func_name):
	"""
	help function to call functions through user entered command
	if function name exists then call and return true
	"""
	method = getattr(current_module, func_name, None)
	if method:
		method()
		return True

if __name__ == "__main__":
	# format documents
	for action in parser._actions:
		method = getattr(current_module, action.dest, None)
		if method:
			method.__doc__ = method.__doc__.format(
				help=action.help, usageprefix=usage_prefix, pathprefix=PATHPREFIX)
	# excute command,if command is not correct print help
	if len(argv)<=1 or not __call(argv[1]):
		parser.parse_args([argv[0], "-h"])