#encoding:utf8
from copy import copy
from httputils import HTTPSConnection, encode_multipart_formdata, params_generate

__all__ = [
	"File",
	"ApiClient",
	"BaiduOpenApi",
	"BaiduOpenApiException",
	"BaiduPCS",
	"BaiduPCSException"
]

# def safe_quote(arg):
# 	"""
# 	quote all characters in url params
# 	"""
# 	try:
# 		from urllib.parse import quote
# 	except ImportError:
# 		from urllib import quote
# 	return quote(arg, "")

class File:
	"""
	Explicit the post value if file.
	"""
	def __init__(self, filename, value):
		self.filename = filename
		self.value = value

class RequestBase:
	"""
	http method class
	"""
	def __init__(self, base_url, method="GET", route="", params=None, headers=None, 
		body=None, caller=None):
		# default request vars
		self.base_url = base_url
		self.method = method
		self.route = route
		self.params = params or {}
		self.headers = headers or {}
		self.body = body
		self.raw = False
		self.caller = caller

	def getresponse(self):
		"""
		make http request and get response
		this method must not change fields in this instance
		because we may call this method again in error handler
		"""
		with HTTPSConnection(self.base_url) as conn:
			conn.request(self.method, self.route + params_generate(**self.params), 
				headers=self.headers, body=self.body)
			try:
				resp = conn.getresponse()
			except TimeoutError:
				return self.getresponse()
			if resp.status >= 400:
				return self.caller.exception_handler(resp, self)
			content = resp.read()
			return content if self.raw else eval(content)

	def __repr__(self):
		return "{method} {base_url}{route}{params}".format(
			method=self.method.upper(), base_url=self.base_url, route=self.route, 
			params=params_generate(**self.params))

	def __str__(self):
		return self.__repr__()

class GetRequest(RequestBase):
	"""
	make a http get request
	"""
	def __call__(self, **kwargs):
		self.method = "GET"
		self.params.update(kwargs)
		return super(GetRequest, self).getresponse()

class PostRequest(RequestBase):
	"""
	make a post request(encode_multipart_formdata)
	"""
	def __call__(self, **kwargs):
		self.method = "POST"
		# if files, place other params in url
		files = [(k, v.filename, v.value) for k, v in kwargs.items() if isinstance(v, File)]
		params = {k: v for k, v in kwargs.items() if not isinstance(v, File)}
		fields = self.params.update(params) if files else params.items()
		# # 要把method单独挑出来 有待改善
		# if files:
		# 	self.params.update(params)
		# else:
		# 	self.params["method"] = params["method"]
		#	fields = [item for item in kwargs.items() if item[0] != "method"]
		# make multi-part form body
		self.body, boundary = encode_multipart_formdata(fields=fields, files=files)
		self.headers["Content-Length"] = len(self.body)
		self.headers["Content-Type"] = "multipart/form-data; boundary=%s"%boundary
		# else place all params in body
		return super(PostRequest, self).getresponse()

	def __repr__(self):
		rep = super(PostRequest, self).__repr__()
		if self.body:
			rep = rep + "\tBODY：{body}".format(body=self.body[:512])
		return rep

http_methods = {"get": GetRequest, "post": PostRequest}

class ApiClient:
	"""
	Creating http request or continue mapping instance to restful api.
	In this case, the content of post http body is multipart/form-data.
	"""
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
			self.__attrs__[attr] = self.init_request(http_methods[attr]) \
				if attr in http_methods else self.__class__(self.route + '/' + attr)
		return self.__attrs__[attr]

	@property
	def url(self):
		"""
		Return full url of this api.
		"""
		self.base_url.strip('/') + self.route

from clients.baiduopenapi import *
from clients.baidupcs import *