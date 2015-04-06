#encoding:utf8
import os
from unittest import TestCase

# change base path to test folder
from config import config
config.PATHPREFIX = config.TESTFOLDER
config.PIECE = 256*1024
config.PIECES = 2
import logging
oldHandler = logging.getLogger().handlers[0]
newHandler = logging.FileHandler(config.TESTLOGFILE)
newHandler.setFormatter(oldHandler.formatter)
logging.getLogger().handlers[0] = newHandler


__all__ = ["BaseTest"]

class BaseTest(TestCase):
	"""
	base class of tests
	"""
	def setUp(self):		
		# create test folder
		from services.pcsservice import delete, mkdir
		delete('/', True)
		mkdir('/')

	def tearDown(self):
		# delete test folder
		from services.pcsservice import delete
		delete('/', True)