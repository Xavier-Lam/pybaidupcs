#encoding:utf8

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging
import os
from sys import argv, modules
import time
from clients import BaiduOpenApiException, BaiduPCSException
from config import config
from console.utils import bytes2human

current_module = modules[__name__]
usage_prefix = "python3 tsguploader.py"

# logging
logging.basicConfig(filename=config.LOGFILE, level=logging.INFO,
	format="[%(levelname)s] %(asctime)s: %(message)s")

parser = ArgumentParser(description="""  TSGUploader 
  A baiduyun toolkit written in python use baidu rest api.
  Written by Xavier-Lam(13599838712@hotmail.com)
  Home page: https://github.com/Xavier-Lam/pybaidupcs
  WARNING: This program seems not support Chinese filenames""", 
	usage=usage_prefix + " [COMMAND] [OPTION]... [ARGS]...",
	formatter_class=RawDescriptionHelpFormatter)

# just for print description
parser.add_argument("cp", help="cp files and directories")
parser.add_argument("dl", help="a simple download implement")
parser.add_argument("info", help="show file infomation")
parser.add_argument("init", help="get user authorization")
parser.add_argument("ls", help="list directory contents")
parser.add_argument("mkdir", help="make directories")
parser.add_argument("mv", help="move (rename) files")
parser.add_argument("rm", help="remove files or directories")
parser.add_argument("test", help="run unit test")
parser.add_argument("upload", help="upload files to baiduyun")

def __error_handler(func):
	"""
	handle errors
	"""
	from functools import wraps
	@wraps(func)
	def decorated_func(*args, **kwargs):
		try:
			from http.client import HTTPException
		except ImportError:
			from httplib import HTTPException
		from common import ApplicationException
		try:
			return func(*args, **kwargs)
		except BaiduPCSException as e:
			print("ERROR {0}".format(str(e)))
		except ApplicationException as e:
			logging.error(str(e.args[0]))
			print(e.args[0])
		except BaiduOpenApiException as e:
			print("ERROR {0}\nIf this problem show up constantly, try init.".format(str(e)))
		except HTTPException as e:
			print(e.args[0] + "please check up log for more information.")
	return decorated_func

@__error_handler
def cp():
	""" {help}
	{usageprefix} cp [OPTION] FROM TO
	WARNING: files are under {pathprefix}"""
	parser = ArgumentParser(usage=cp.__doc__)
	parser.add_argument("-f", "--force", action="store_true", 
		help="remove destination file if exists.")
	parser.add_argument("from_", help="file or directory path")
	parser.add_argument("to", help="file or directory path")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcs import copy
	copy(args.from_, args.to, args.force)

@__error_handler
def dl():
	""" {help}
	{usageprefix} dl [OPTION] DOWNLOADPATH LOCALPATH
	WARNING: files are under {pathprefix}"""
	parser = ArgumentParser(usage=dl.__doc__)
	parser.add_argument("-f", "--force", action="store_true",
		help="override local file if exists")
	parser.add_argument("-i", "--interactive", action="store_true",
		help="prompt if localfile exists")
	parser.add_argument("-r", "--resume", action="store_true",
		help="resume incompleted download")
	parser.add_argument("downloadpath", help="download from")
	parser.add_argument("localpath", help="localpath to store file")
	args, _ = parser.parse_known_args(argv[2:])

	if args.interactive and os.path.isfile(args.localpath):
		# if file exist
		print("local file exists, if this is a incompleted download file please"
			" enter r, if you want to override this file enter y, if you don't want"
			" to override this file enter other keys")
		res = input().lower()
		if res == 'r':
			args.resume = True
		elif res == 'y':
			args.force = True
		else:
			return
	from services.pcs import Download
	with Download(args.downloadpath, args.localpath) as download:
		download.progress_callback = lambda x: print("%.2f%%"%x)
		download(override=args.force, resume=args.resume)

# def video_encode():
# 	from services.pcs import encode
# 	a = encode("1.ts")
# 	print(a)

@__error_handler
def info():
	""" {help}
	{usageprefix} info FILEPATH
	WARNING: files are under {pathprefix}"""
	parser = ArgumentParser(usage=info.__doc__)
	parser.add_argument("filepath", help="file or directory path")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcs import fileinfo, safe_path
	f = fileinfo(args.filepath)
	print("{0:20}\t{1}".format("path", safe_path(f["path"])))
	print("{0:20}\t{1}".format("directory", bool(f["isdir"])))
	print("{0:20}\t{1}".format("sub directory", bool(f["ifhassubdir"])))
	print("{0:20}\t{1}".format("size", bytes2human(f["size"])))
	print("{0:20}\t{1}".format("create_time", 
		time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(f["ctime"]))))
	print("{0:20}\t{1}".format("modify_time", 
		time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(f["mtime"]))))

def init():
	""" {help}
	"""
	from services.openapi import apply_auth
	for i in apply_auth():
		print("please wait")

@__error_handler
def ls():
	""" {help}
	{usageprefix} ls DIRECTORY
	WARNING: files are under {pathprefix}"""
	parser = ArgumentParser(usage=ls.__doc__)
	parser.add_argument("directory", help="directory name", default='/')
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcs import listfiles
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

@__error_handler
def mkdir():
	""" {help}
	{usageprefix} mkdir DIRECTORY
	WARNING: directory is under {pathprefix}"""
	parser = ArgumentParser(usage=mkdir.__doc__)
	parser.add_argument("directory", help="directory name")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcs import mkdir as mkdirservice
	mkdirservice(args.directory)

@__error_handler
def mv():
	""" {help}
	{usageprefix} mv [OPTION] FROM TO
	WARNING: files are under {pathprefix}"""
	parser = ArgumentParser(usage=mv.__doc__)
	parser.add_argument("-f", "--force", action="store_true", 
		help="remove destination file if exists.")
	parser.add_argument("from_", help="file or directory path")
	parser.add_argument("to", help="file or directory path")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcs import move
	move(args.from_, args.to, args.force)

@__error_handler
def rm():
	""" {help}
	{usageprefix} rm [OPTION] FILEPATHS
	WARNING: files are under {pathprefix}"""
	parser = ArgumentParser(usage=rm.__doc__)
	parser.add_argument("-f", "--force", action="store_true", 
		help="ignore nonexistent files")
	parser.add_argument("filepaths", help="file or directory path", nargs="+")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcs import delete
	delete(args.filepaths, args.force)

def test():
	""" {help}
	{usageprefix} test
	"""
	import logging
	from unittest import TestLoader, TextTestRunner
	print("sometimes these tests may not pass. I don't know why...")
	TextTestRunner(verbosity=2).run(TestLoader().discover("tests"))
	logging.info("test ends")

@__error_handler
def upload():
	""" {help}
	{usageprefix} upload [OPTION] LOCALPATH UPLOADPATH
	WARNING: uploadpath is under {pathprefix}"""
	parser = ArgumentParser(usage=upload.__doc__)
	parser.add_argument("-f", "--force", action="store_true", 
		help="remove destination file if exists")
	parser.add_argument("-d", "--direct", action="store_false", 
		help="upload file directly without check rapid upload")
	parser.add_argument("localpath", help="file path")
	parser.add_argument("uploadpath", help="upload path")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcs import Upload
	with Upload(args.localpath, args.uploadpath) as upload_:
		upload_.progress_callback = lambda x: print("%.2f%%"%x)
		upload_(force=args.force, rapid=args.direct)

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
				help=action.help, usageprefix=usage_prefix, pathprefix=config.PATHPREFIX)
	# excute command,if command is not correct print help
	if len(argv)<=1 or not __call(argv[1]):
		parser.parse_args([argv[0], "-h"])