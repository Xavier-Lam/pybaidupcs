#encoding:utf8
import os

__all__ = ["Config"]

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class ConfigBase(object):
	def update(self, configs):
		for k, v in configs.items():
			setattr(self, k, v)

	def __getitem__(self, key):
		return getattr(self, key)

	def __setitem__(self, key, value):
		setattr(self, key, value)

	def get(self, key, default=None):
		return getattr(self, key, default)

class Config(ConfigBase):
	USAGE_PREFIX = "python3 pybaidupcs"

	# input your api key here
	BAIDU_API_KEY = "4OySt4LBqrR6QNyo7yXywsnC"#os.environ["BAIDU_API_KEY"]
	BAIDU_SECRET_KEY = "GQhhC485PAejjST6HiAPbG0kTCSlrxWW"#os.environ["BAIDU_SECRET_KEY"]
	# name of your app
	APPNAME = "TSGUploader"
	# path to store your token
	TOKENPATH = os.path.join(BASE_FOLDER, r"authorization.json")
	# baiduyun path prefix
	PATHPREFIX = "/apps" + '/' + APPNAME.lower()

	# max simple upload size (bytes)
	UPLOADPIECE = 512*1024
	# 2 ~ 1024
	UPLOADPIECES = 1024
	# max download piece size
	DOWNLOADPIECE = 512*1024

	#loging path
	LOGFILE = os.path.join(BASE_FOLDER, r"log.log")
	TESTLOGFILE = os.path.join(BASE_FOLDER, r"test_log.log")

	# folder to store temporary file
	TEMPFILEFOLDER = "/__tmp_"
	# folder to run unit test
	TESTFOLDER = PATHPREFIX + TEMPFILEFOLDER + "/__test_"

config = Config()