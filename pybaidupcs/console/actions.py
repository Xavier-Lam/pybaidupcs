#encoding:utf8
from __future__ import print_function
from argparse import ArgumentParser
import logging
import os
from sys import argv, modules
import time
from clients import BaiduOpenApiException, BaiduPCSException
from common import ApplicationException
from config import config
from console.intro import parser
from console.utils import bytes2human

__all__ = [
	"cp",
	"dl",
	"find",
	"info",
	"init",
	"ls",
	"mkdir",
	"mv",
	"rm",
	"test",
	"upload"
]

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
		try:
			return func(*args, **kwargs)
		except BaiduPCSException as e:
			print("ERROR {0}".format(str(e)))
		except ApplicationException as e:
			logging.error(str(e.args[0]))
			print(e.args[0])
		except BaiduOpenApiException as e:
			print("ERROR {0}\nIf this problem show up constantly, try init."\
				.format(str(e)))
		except HTTPException as e:
			print(e.args[0] + "please check up log for more information.")
	return decorated_func

def formatfiles(files):
	for f in files:
		# transfer timestamp to time string
		mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(f["mtime"]))
		# if isdir then size display as <dir> else print size
		size = "<dir>" if f["isdir"] else bytes2human(f["size"])
		# erase path prefix
		try:
			print("{mtime:20} {size:10} {filename}"\
				.format(mtime=mtime, size=size, filename=f["path"]))
		except UnicodeEncodeError as e:
			raise ApplicationException("something wrong with your file, please rename"
				+ f["path"])

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

@__error_handler
def find():
	""" {help}
	{usageprefix} find [-p SEARCHPATH] KEYWORD
	WARNING: files are under {pathprefix}"""
	parser = ArgumentParser(usage=find.__doc__)
	parser.add_argument("-p", "--path", nargs='?', help="search path", default="/")
	parser.add_argument("keyword", help="keyword")
	args, _ = parser.parse_known_args(argv[2:])

	from services.pcs import find as find_files
	files = find_files(args.keyword, args.path)
	formatfiles(files)

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

@__error_handler
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
	for file in files:
		file["path"] = os.path.split(file["path"])[1]
	formatfiles(files)

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
	import tests
	print("sometimes these tests may not pass. I don't know why...")
	TextTestRunner(verbosity=2).run(TestLoader().loadTestsFromModule(tests))
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

# format documents
for action in parser._actions:
	method = getattr(modules[__name__], action.dest, None)
	if method:
		method.__doc__ = method.__doc__.format(help=action.help, 
			usageprefix=config.USAGE_PREFIX, pathprefix=config.PATHPREFIX)