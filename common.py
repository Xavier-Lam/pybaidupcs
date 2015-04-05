#encoding:utf8
class CloseableClass:
	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.close()