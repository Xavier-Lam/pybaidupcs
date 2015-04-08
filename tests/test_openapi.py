#encoding:utf8
import logging
from tests import BaseTest

__all__ = ["OpenApiTest"]

class OpenApiTest(BaseTest):
	"""
	test open api
	"""
	def test_invalidtoken(self):
		from clients import BaiduPCS
		logging.info("------invalidtoken------")
		client = BaiduPCS()
		BaiduPCS.access_token = "invalidtoken"
		from services.pcs import listfiles
		listfiles("/")

	def test_refreshtoken(self):
		from clients import BaiduPCS
		logging.info("------refreshtoken------")
		client = BaiduPCS()
		from services.openapi import refresh_tokens
		refresh_tokens(client.refresh_token)
		from services.pcs import listfiles
		listfiles("/")