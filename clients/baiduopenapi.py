#encoding:utf-8
try:
	from http.client import HTTPException
except ImportError:
	from httplib import HTTPException
from clients import ApiClient
from config import BAIDU_API_KEY, BAIDU_SECRET_KEY

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
		kwargs["client_id"] = BAIDU_API_KEY
		kwargs["client_secret"] = BAIDU_SECRET_KEY
		self.route = "/oauth/2.0" + self.route
		return super(BaiduOpenApi, self).get(**kwargs)

	def exception_handler(self, resp, method, kwargs):
		"""
		handle exception from response.
		"""
		try:
			msg = eval(resp.read())
		except:
			raise HTTPException("unexcept response.")
		raise BaiduOpenApiException(resp.status, **msg)