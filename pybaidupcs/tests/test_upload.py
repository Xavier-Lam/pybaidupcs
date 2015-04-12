#encoding:utf8
import logging
from services.pcs import check_rapidupload, rapidupload_info, Upload
from tests import BaseTest

__all__ = ["UploadTest"]

class UploadTest(BaseTest):
	"""
	test upload methods
	"""
	def __init__(self, *args, **kwargs):
		super(UploadTest, self).__init__(*args, **kwargs)
		import os
		from config import BASE_FOLDER
		test_folder = os.path.join(BASE_FOLDER, "tests")
		self.smallfile = os.path.join(test_folder, "smallfile")
		self.bigfile = os.path.join(test_folder, "bigfile")
		self.largefile = os.path.join(test_folder, "largefile")
		try:
			os.mkdir(test_folder)
			with open(self.smallfile, 'w') as f:
				f.write(200*1024*'a')
			with open(self.bigfile, 'w') as f:
				f.write(500*1024*'a')
			with open(self.largefile, 'w') as f:
				f.write(1200*1024*'a')
		except Exception as e:
			pass

	def test_upload_smallfile(self):
		logging.info("------upload_smallfile------")
		with Upload(self.smallfile, "smallfile") as upload:
			upload._prepare()
			upload._singleupload()

	def test_upload_bigfile(self):
		logging.info("------upload_bigfile------")
		with Upload(self.bigfile, "bigfile") as upload:
			upload._prepare()
			upload._multiupload()

	def test_upload_largefile(self):
		logging.info("------upload_largefile------")
		with Upload(self.largefile, "largefile") as upload:
			upload._prepare()
			upload._multiupload()

	def test_rapidupload(self):
		logging.info("------upload_rapidupload------")
		info = rapidupload_info(self.largefile)
		self.assertTrue(check_rapidupload(uploadpath="rapidfile", **info))