#encoding:utf8
import os
from unittest import TestCase

__all__ = ["BaseTest"]

class BaseTest(TestCase):
	"""
	base class of tests
	"""
	def setUp(self):
		# change base path to test folder
		from config import config
		config.PATHPREFIX = config.TESTFOLDER
		# create test folder
		from services.pcsservice import delete, mkdir
		try:
			delete('/')
		except:
			pass
		mkdir('/')

	def tearDown(self):
		# delete test folder
		from services.pcsservice import delete
		try:
			delete('/')
		except:
			pass