#encoding:utf-8
try:
	from http.client import HTTPException
except ImportError:
	from httplib import HTTPException
from clients import ApiClient
from config import config

__all__ = [
	"BaiduOpenApiException",
	"BaiduOpenApi"
]

class BaiduOpenApiException(Exception):
	"""
	packaged baidu open api exception
	"""
	def __init__(self, status, error, error_description):
		self.status = status
		self.error = error
		self.error_description = error_description

	def __repr__(self):
		return "{error}({status}): {desc}"\
			.format(error=self.error, status=self.status, desc=self.error_description)

	def __str__(self):
		return self.__repr__()

class BaiduOpenApi(ApiClient):
	"""
	BaiduOpenApi Client.
	"""
	base_url = "openapi.baidu.com"

	def get(self, **kwargs):
		"""
		overwrite get method for add clientid and secretid.
		and add api prefix /oauth/2.0
		"""
		kwargs["client_id"] = config.BAIDU_API_KEY
		kwargs["client_secret"] = config.BAIDU_SECRET_KEY
		self.route = "/oauth/2.0" + self.route
		return super(BaiduOpenApi, self).get(**kwargs)

	def exception_handler(self, resp, method, kwargs):
		"""
		handle exception from response.
		"""
		import logging
		try:
			msg = eval(resp.read())
		except Exception as e:
			logging.error(str(e))
			raise HTTPException("unexcept response.", e)
		error = BaiduOpenApiException(resp.status, **msg)
		logging.warning("{error}=>({method} {route} {kwargs})".format(error=str(error), 
			method=method.__name__.upper(), route=self.route, kwargs=str(kwargs)))
		raise error

	def __repr__(self):
		return "<BaiduOpenApi %s>"%self.route