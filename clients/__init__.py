#encoding:utf8
from copy import copy
from clients.request import *
from httputils import HTTPSConnection, encode_multipart_formdata, params_generate

__all__ = [
	"File",
	"ApiClient",
	"BaiduOpenApi",
	"BaiduOpenApiException",
	"BaiduPCS",
	"BaiduPCSException",
	"GetRequest",
	"PostMultiPartFormRequest"
]

class ApiClient(object):
	"""
	Creating http request or continue mapping instance to restful api.
	In this case, the content of post http body is multipart/form-data.
	"""
	HTTPMETHODS = {"get": GetRequest, "post":PostMultiPartFormRequest}

	def __init__(self, route=""):
		"""
		Building route of this api.
		"""
		self.route = route
		self.__attrs__ = dict()

	def __getattr__(self, attr):
		"""
		Return sub api or make request
		"""
		# if route is not defined return empty string
		if not attr in self.__attrs__:
			# judge make request or return subapi
			self.__attrs__[attr] = self.init_request(self.HTTPMETHODS[attr]) \
				if attr in self.HTTPMETHODS else self.__class__(self.route + '/' + attr)
		return self.__attrs__[attr]

	@property
	def url(self):
		"""
		Return full url of this api.
		"""
		self.base_url.strip('/') + self.route

from clients.baiduopenapi import *
from clients.baidupcs import *