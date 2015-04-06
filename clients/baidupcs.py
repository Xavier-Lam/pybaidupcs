#encoding:utf-8
try:
	from http.client import HTTPException
except ImportError:
	from httplib import HTTPException
from clients import ApiClient

__all__ = [
	"BaiduPCSException",
	"BaiduPCS"
]

class BaiduPCSException(Exception):
	"""
	packaged baidu pcs exception.
	"""
	def __init__(self, status, error_code, error_msg):
		self.status = status
		self.error_code = error_code
		self.error_msg = error_msg

	def __repr__(self):
		return "[{errorcode}]: {errormsg}({status})"\
				.format(errorcode=self.error_code, errormsg=self.error_msg, status=self.status)

	def __str__(self):
		return self.__repr__()

class BaiduPCS(ApiClient):
	"""
	BaiduPCS api client.
	"""
	base_url = "pcs.baidu.com"
	access_token = None
	refresh_token = None

	def __init__(self, route=""):
		from services.openapiservice import deserialize_tokens
		# if there is no tokens load
		if not BaiduPCS.access_token:
			# load tokens from harddisk
			BaiduPCS.access_token, BaiduPCS.refresh_token = deserialize_tokens()
		super(BaiduPCS, self).__init__(route)

	def get(self, **kwargs):
		"""
		overwrite get method for accesstoken maintained by self
		and add api prefix /rest/2.0
		"""
		kwargs["access_token"] = self.access_token
		self.route = "/rest/2.0" + self.route
		return super(BaiduPCS, self).get(**kwargs)

	def post(self, **kwargs):
		"""
		overwrite post method for accesstoken maintained by self.
		and add api prefix /rest/2.0
		"""
		kwargs["access_token"] = self.access_token
		self.route = "/rest/2.0" + self.route
		return super(BaiduPCS, self).post(**kwargs)

	def exception_handler(self, resp, method, kwargs):
		"""
		handle exception from response.
		input:
			resp	response instance
			method	which method raised exception
			kwargs	args which caused exception
		"""
		import logging
		try:
			msg = eval(resp.read())
			# if accesstoken expired
			# refresh accesstoken and recall method and return
			if resp.status == 401:
				logging.info("access token has expired.")
				from services.openapiservice import refresh_tokens
				BaiduPCS.access_token, BaiduPCS.refresh_token = refresh_tokens(BaiduPCS.refresh_token)
				kwargs["access_token"] = BaiduPCS.access_token
				return method(**kwargs)
		except Exception as e:
			logging.error(str(e))
			raise HTTPException("unexcept response.", e)
		error = BaiduPCSException(resp.status, msg["error_code"], msg["error_msg"])
		logging.warning("{error}=>({method} {route} {kwargs})".format(error=str(error), 
			method=method.__name__.upper(), route=self.route, kwargs=str(kwargs)))
		raise error

	def __repr__(self):
		return "<BaiduPCS %s>"%self.route