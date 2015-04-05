#encoding:utf8
try:
	import http.client as httplib
except ImportError:
	import httplib
import mimetypes

__all__ = [
	"HTTPSConnection",
	"encode_multipart_formdata",
	"params_generate"
]

class HTTPSConnection(httplib.HTTPSConnection):
	"""
	decorate HTTPSConnection with __enter__ and __exit__
	"""
	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.close()

def boundary_generate():
	"""
	generate boundary
	"""
	# res = '-'*24 + "tsguploader" + md5(str(time.time()).encode()).hexdigest()
	# return res.encode()
	return "-------------------------acebdf13572468"

def get_contenttype(filename):
	return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def encode_multipart_formdata(fields=[], files=[]):
	"""
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for
	data to be uploaded as files
	Return (body, boundary) 
	"""
	boundary = boundary_generate()
	L = []
	for (key, value) in fields:
		L.append(bytes("--" + boundary,"ASCII"))
		L.append(bytes('Content-Disposition: form-data; name="%s"' % key,"ASCII"))
		L.append(b'')
		L.append(bytes(str(value),"ASCII"))
	for (key, filename, value) in files:
		L.append(bytes('--' + boundary,"ASCII"))
		L.append(bytes('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename),"ASCII"))
		L.append(bytes('Content-Type: %s' % get_contenttype(filename),"ASCII"))
		L.append(b'')
		L.append(value)
	L.append(bytes('--' + boundary + '--',"ASCII"))
	L.append(b'')
	body = bytes("\r\n","ASCII").join(L)
	# content_type = 'multipart/form-data; boundary=' + boundary
	return body, boundary

def params_generate(**kwargs):
	"""
	generate url param like ?prefix=xxx&marker=xxx
	"""
	param_str = [ '='.join(map(str, key_value)) for key_value in kwargs.items() if key_value[1] != None]
	res = "" if not len(param_str) else '?' + '&'.join(param_str)
	return res