#encoding:utf8
try:
	import http.client as httplib
except ImportError:
	import httplib
import mimetypes
from common import CloseableClass

__all__ = [
	"HTTPSConnection",
	"encode_multipart_formdata",
	"params_generate"
]

class HTTPSConnection(httplib.HTTPSConnection, CloseableClass):
	"""
	decorate HTTPSConnection with __enter__ and __exit__
	"""
	pass

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
	param_str = [str(k) + '=' + str(v) for k, v in kwargs.items() if v != None]
	return '?' + '&'.join(param_str) if param_str else ""