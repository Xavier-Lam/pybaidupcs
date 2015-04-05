#encoding:utf8
import os
from unittest import TestCase
from tests import BaseTest

__all__ = ["FileSysTest"]

getfilename = lambda x: os.path.split(x)[1]

class FileSysTest(BaseTest):
	"""
	test pcs methods
	"""
	def test1_mkdir(self):
		from clients import BaiduPCSException
		from services.pcsservice import listfiles, mkdir
		mkdir("aaa")
		mkdir("bbb")
		mkdir("aaa\\aaa")
		mkdir("aaa/bbb")
		files = listfiles("/")
		files = {getfilename(f["path"]):f["isdir"] for f in files}
		# there are only two files
		self.assertTrue(len(files)==2)
		# their names are aaa, bbb and they are directories
		self.assertTrue("aaa" in files.keys() and "bbb" in files.keys())
		self.assertTrue(1 in files.values() and 0 not in files.values())
		# there are only two files under aaa
		files = listfiles("/aaa")
		files = {getfilename(f["path"]):f["isdir"] for f in files}
		# there are only two files
		self.assertTrue(len(files)==2)
		# their names are aaa, bbb and they are directories
		self.assertTrue("aaa" in files.keys() and "bbb" in files.keys())
		self.assertTrue(1 in files.values() and 0 not in files.values())
		# you cannot make a directory has same name with bbb
		self.assertRaises(BaiduPCSException, mkdir, "bbb")

	def test2_cp(self):
		from clients import BaiduPCSException
		from services.pcsservice import listfiles, copy
		raise Exception(listfiles("/"))
		copy("aaa", "ccc")
		files = listfiles("/")
		files = {getfilename(f["path"]):f["isdir"] for f in files}
		# there are only three files include "ccc"
		self.assertTrue(len(files)==3 and "ccc" in files.keys())
		# in ccc there are only aaa, bbb
		files = listfiles("/ccc")
		files = {getfilename(f["path"]):f["isdir"] for f in files}
		# there are only two files
		self.assertTrue(len(files)==2)
		# their names are aaa, bbb and they are directories
		self.assertTrue("aaa" in files.keys() and "bbb" in files.keys())
		self.assertTrue(1 in files.values() and 0 not in files.values())
		# you cannot copy a directory has same name with ccc
		self.assertRaises(BaiduPCSException, mkdir, "bbb", "ccc")

	# def test3_mv(self):
	# 	from clients import BaiduPCSException
	# 	from services.pcsservice import listfiles, move
	# 	move("ccc", "bbb/ccc")
	# 	files = listfiles("/")
	# 	files = {getfilename(f["path"]):f["isdir"] for f in files}
	# 	# there are only two files under root
	# 	self.assertTrue(len(files)==2)
	# 	# their names are aaa, bbb and they are directories
	# 	self.assertTrue("aaa" in files.keys() and "bbb" in files.keys())
	# 	self.assertTrue(1 in files.values() and 0 not in files.values())
	# 	files = listfiles("\\bbb")
	# 	files = {getfilename(f["path"]):f["isdir"] for f in files}
	# 	# there are only three files include "ccc"
	# 	self.assertTrue(len(files)==1 and "ccc" in files.keys())
	# 	# in ccc there are only aaa, bbb
	# 	files = listfiles("bbb/ccc")
	# 	files = {getfilename(f["path"]):f["isdir"] for f in files}
	# 	# there are only two files
	# 	self.assertTrue(len(files)==2)
	# 	# their names are aaa, bbb and they are directories
	# 	self.assertTrue("aaa" in files.keys() and "bbb" in files.keys())
	# 	self.assertTrue(1 in files.values() and 0 not in files.values())
	# 	# you cannot copy a directory has same name with ccc
	# 	self.assertRaises(BaiduPCSException, mkdir, "aaa", "bbb\\ccc")

	# def test4_rm(self):
	# 	from clients import BaiduPCSException
	# 	from services.pcsservice import listfiles, delete
	# 	delete("aaa")
	# 	# there are only bbb under root
	# 	self.assertTrue(len(files)==1)
	# 	self.assertTrue("aaa" not in files.keys() and "bbb" in files.keys())
	# 	# you cannot delete a unexist file
	# 	self.assertRaises(BaiduPCSException, delete, "aaa")