#encoding:utf8
from sys import argv
import console.actions
from console.intro import *

def __call(func_name):
	"""
	help function to call functions through user entered command
	if function name exists then call and return true
	"""
	method = getattr(console.actions, func_name, None)
	if method:
		method()
		return True

def run():
	# excute command,if command is not correct print help
	if len(argv)<=1 or not __call(argv[1]):
		show_help()