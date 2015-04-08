#encoding:utf8
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from config import config

__all__ = ["show_help", "parser"]

parser = ArgumentParser(description="""  TSGUploader 
  A baiduyun toolkit written in python use baidu rest api.
  Written by Xavier-Lam(13599838712@hotmail.com)
  Home page: https://github.com/Xavier-Lam/pybaidupcs
  WARNING: This program seems not support Chinese filenames very well""", 
	usage=config.USAGE_PREFIX + " [COMMAND] [OPTION]... [ARGS]...",
	formatter_class=RawDescriptionHelpFormatter)

# just for print description
parser.add_argument("cp", help="cp files and directories")
parser.add_argument("dl", help="a simple download implement")
parser.add_argument("find", help="find a file")
parser.add_argument("info", help="show file infomation")
parser.add_argument("init", help="get user authorization")
parser.add_argument("ls", help="list directory contents")
parser.add_argument("mkdir", help="make directories")
parser.add_argument("mv", help="move (rename) files")
parser.add_argument("rm", help="remove files or directories")
parser.add_argument("test", help="run unit test")
parser.add_argument("upload", help="upload files to baiduyun")

def show_help():
	parser.parse_args(["-h"])