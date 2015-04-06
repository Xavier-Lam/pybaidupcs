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
	def test_mkdir(self):
		from clients import BaiduPCSException
		from services.pcsservice import fileinfo, mkdir, safe_path
		# case1 make a directory aaa
		mkdir("aaa")
		info = fileinfo("\\aaa")
		self.assertTrue(safe_path(info["path"])==safe_path("/aaa") and info["isdir"])
		# case2 make a directory bbb under aaa
		mkdir("/aaa/bbb")
		info = fileinfo("\\aaa\\bbb")
		self.assertTrue(safe_path(info["path"])==safe_path("/aaa/bbb") and info["isdir"])
		# case3 make a directory has same name with aaa
		self.assertRaises(BaiduPCSException, mkdir, "aaa")

	def test_cp(self):
		from clients import BaiduPCSException
		from services.pcsservice import copy, fileinfo, listfiles, mkdir, safe_path
		# case1 copy aaa to bbb
		mkdir("aaa")
		copy("aaa", "/bbb")
		files = listfiles('/')
		filenames = [safe_path(file["path"]) for file in files]
		self.assertTrue(safe_path("/aaa") in filenames and safe_path("\\bbb") in filenames)
		# case2 copy bbb to aaa/bbb
		copy("bbb", "\\aaa\\bbb")
		info = fileinfo("/aaa/bbb")
		self.assertTrue(safe_path(info["path"])==safe_path("\\aaa\\bbb") and info["isdir"])
		# case3 copy bbb to aaa
		self.assertRaises(BaiduPCSException, copy, "bbb", "aaa")
		# case4 force copy bbb to aaa
		copy("bbb", "aaa", True)
		self.assertTrue(len(listfiles("/"))==2)
		info = fileinfo("aaa")
		self.assertTrue(info["ifhassubdir"]==0)

	def test_mv(self):
		from clients import BaiduPCSException
		from services.pcsservice import move, fileinfo, listfiles, mkdir, safe_path
		# case1 move aaa to bbb
		mkdir("aaa")
		move("/aaa", "\\bbb")
		files = listfiles('/')
		self.assertTrue(len(files)==1 and safe_path(files[0]["path"])==safe_path("/bbb"))
		# case2 move aaa to bbb/bbb
		mkdir("aaa")
		move("/aaa", "\\bbb\\bbb")
		files = listfiles('/')
		self.assertTrue(len(files)==1 and safe_path(files[0]["path"])==safe_path("/bbb"))
		files = listfiles("/bbb")
		self.assertTrue(len(files)==1 and safe_path(files[0]["path"])==safe_path("\\bbb\\bbb"))
		# case3 move aaa to bbb
		mkdir("aaa")
		self.assertRaises(BaiduPCSException, move, "aaa", "bbb")
		# case4 force move aaa to bbb
		move("aaa", "\\bbb", True)
		files = listfiles('/')
		info = fileinfo("bbb")
		self.assertTrue(len(files)==1 and safe_path(files[0]["path"])==safe_path("/bbb"))
		self.assertTrue(info["ifhassubdir"]==0)

	def test_rm(self):
		from clients import BaiduPCSException
		from services.pcsservice import delete, fileinfo, listfiles, mkdir, safe_path
		# case1 delete aaa
		mkdir("/aaa")
		delete("aaa")
		self.assertFalse(listfiles('/'))
		# case2 delete a nonexist directory
		self.assertRaises(BaiduPCSException, delete, "\\aaa")
		# case3 force delete a nonexist directory
		delete("aaa", True)