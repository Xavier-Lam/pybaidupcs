#encoding:utf8
class ApplicationException(Exception):
	pass

class CloseableClass(object):
	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.close()