#encoding:utf8

class ConsoleColours(object):
	"""
	help class for console to print colourful text
	"""
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	@classmethod
	def bold(cls, string):
		return cls.BOLD + string + cls.ENDC

	@classmethod
	def green(cls, string):
		return cls.OKGREEN + string + cls.ENDC

def bytes2human(n, format='%(value).1f %(symbol)s', symbols='customary'):
		"""
		Convert n bytes into a human readable string based on format.
		symbols can be either "customary", "customary_ext", "iec" or "iec_ext",
		see: http://goo.gl/kTQMs

			>>> bytes2human(0)
			'0.0 B'
			>>> bytes2human(0.9)
			'0.0 B'
			>>> bytes2human(1)
			'1.0 B'
			>>> bytes2human(1.9)
			'1.0 B'
			>>> bytes2human(1024)
			'1.0 K'
			>>> bytes2human(1048576)
			'1.0 M'
			>>> bytes2human(1099511627776127398123789121)
			'909.5 Y'

			>>> bytes2human(9856, symbols="customary")
			'9.6 K'
			>>> bytes2human(9856, symbols="customary_ext")
			'9.6 kilo'
			>>> bytes2human(9856, symbols="iec")
			'9.6 Ki'
			>>> bytes2human(9856, symbols="iec_ext")
			'9.6 kibi'

			>>> bytes2human(10000, "%(value).1f %(symbol)s/sec")
			'9.8 K/sec'

			>>> # precision can be adjusted by playing with %f operator
			>>> bytes2human(10000, format="%(value).5f %(symbol)s")
			'9.76562 K'
		"""
		SYMBOLS = {
		'customary'		 : ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
		'customary_ext' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
											 'zetta', 'iotta'),
		'iec'					 : ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
		'iec_ext'			 : ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
											 'zebi', 'yobi'),
		}

		n = int(n)
		if n < 0:
				raise ValueError("n < 0")
		symbols = SYMBOLS[symbols]
		prefix = {}
		for i, s in enumerate(symbols[1:]):
				prefix[s] = 1 << (i+1)*10
		for symbol in reversed(symbols[1:]):
				if n >= prefix[symbol]:
						value = float(n) / prefix[symbol]
						return format % locals()
		return format % dict(symbol=symbols[0], value=n)