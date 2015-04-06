#encoding:utf8
from copy import copy
from httputils import HTTPSConnection, encode_multipart_formdata, params_generate

__all__ = [
	"File",
	"ClientBase",
	"ApiClient",
	"BaiduOpenApi",
	"BaiduOpenApiException",
	"BaiduPCS",
	"BaiduPCSException"
]

def safe_quote(arg):
	"""
	quote all characters in url params
	"""
	try:
		from urllib.parse import quote
	except ImportError:
		from urllib import quote
	return quote(arg, "")

class File:
	"""
	Explicit the post value if file.
	"""
	def __init__(self, filename, value):
		self.filename = filename
		self.value = value

class ClientBase:
	"""
	The base abstract class of apiclient.
	"""
	def __init__(self):
		# you can't init this class.
		raise NotImplementedError()

	def __getattr__(self, attr):
		"""
		Return sub api.
		"""
		# if route is not defined return empty string
		return self.__class__(self.route + '/' + attr)

class ApiClient(ClientBase):
	"""
	Creating http request or continue mapping instance to restful api.
	In this case, the content of post http body is multipart/form-data.
	"""
	def __init__(self, route=""):
		"""
		Building route of this api.
		"""
		self.route = route

	@property
	def url(self):
		"""
		Return full url of this api.
		"""
		self.base_url.strip('/') + self.route

	def get(self, **kwargs):
		"""
		Create a get request.
		"""
		o_kwargs = copy(kwargs)
		kwargs = {k:safe_quote(v) for k, v in kwargs.items()}
		with HTTPSConnection(self.base_url) as conn:
			params = params_generate(**kwargs)
			conn.request("GET", self.route + params)
			resp = conn.getresponse()
			if resp.status >= 400:
				return self.exception_handler(resp, super(self.__class__, self).get, o_kwargs)
			return eval(resp.read())

	def post(self, **kwargs):
		"""
		Create a post request.
		"""
		# according to api document,if files in body other params should be in url
		o_kwargs = copy(kwargs)
		files = [(k, v.filename, v.value) for k, v in kwargs.items() if isinstance(v, File)]
		if files:
			kwargs = {k:safe_quote(v) for k, v in kwargs.items() if k not in files[0]}
			params = params_generate(**kwargs)
			fields = []
		else:		
			# method and accesstoken should in url
			params = params_generate(
				method=kwargs.pop("method"), 
				access_token=kwargs.pop("access_token")
			)
			fields = [(k, v) for k, v in kwargs.items()]
		# make multipart formdata
		body, boundary = encode_multipart_formdata(fields=fields, files=files)
		headers = {
				"Content-Length": len(body),
				"Content-Type": "multipart/form-data; boundary=%s"%boundary
			}
		with HTTPSConnection(self.base_url) as conn:
			conn.request("POST", self.route + params, body=body, headers=headers)
			resp = conn.getresponse()
			if resp.status >= 400:
				return self.exception_handler(resp, super(self.__class__, self).post, o_kwargs)
			return eval(resp.read())

from clients.baiduopenapi import *
from clients.baidupcs import *