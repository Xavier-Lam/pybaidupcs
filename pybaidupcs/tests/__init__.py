#encoding:utf8
import os
from unittest import TestCase

# change base path to test folder
from config import config
config.PATHPREFIX = config.TESTFOLDER
config.UPLOADPIECE = 256*1024
config.UPLOADPIECES = 2
import logging
oldHandler = logging.getLogger().handlers[0]
newHandler = logging.FileHandler(config.TESTLOGFILE)
newHandler.setFormatter(oldHandler.formatter)
logging.getLogger().handlers[0] = newHandler
logging.info("test starts")

__all__ = ["BaseTest", "run_test"]

class BaseTest(TestCase):
	"""
	base class of tests
	"""
	def setUp(self):		
		# create test folder
		from services.pcs import delete, mkdir
		delete('/', True)
		mkdir('/')

	def tearDown(self):
		# delete test folder
		from services.pcs import delete
		delete('/', True)

from tests.test_filesys import *
from tests.test_openapi import *
from tests.test_upload import *

# def run_test():
# 	main()