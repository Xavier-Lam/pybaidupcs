#encoding:utf8
from httputils import HTTPSConnection, encode_multipart_formdata, params_generate

__all__ = [
	"File",
	"GetRequest",
	"PostMultiPartFormRequest"
]

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

	def __call__(self, **kwargs):
		return self._call(**kwargs)

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
	def _call(self, **kwargs):
		self.method = "GET"
		self.params.update(kwargs)
		return super(GetRequest, self).getresponse()

class PostMultiPartFormRequest(RequestBase):
	"""
	make a post request(encode_multipart_formdata)
	"""
	def _call(self, **kwargs):
		self.method = "POST"
		# if files, place other params in url
		files = [(k, v.filename, v.value) for k, v in kwargs.items() if isinstance(v, File)]
		params = {k: v for k, v in kwargs.items() if not isinstance(v, File)}
		fields = self.params.update(params) if files else params.items()
		# make multi-part form body
		self.body, boundary = encode_multipart_formdata(fields=fields, files=files)
		self.headers["Content-Length"] = len(self.body)
		self.headers["Content-Type"] = "multipart/form-data; boundary=%s"%boundary
		# else place all params in body
		return super(PostMultiPartFormRequest, self).getresponse()

	def __repr__(self):
		rep = super(PostMultiPartFormRequest, self).__repr__()
		if self.body:
			rep = rep + "\tBODY：{body}".format(body=self.body[:512])
		return rep