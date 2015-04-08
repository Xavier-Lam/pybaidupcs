#encoding:utf8
import logging
from config import config
from console import run

if __name__ == "__main__":
	# logging
	logging.basicConfig(filename=config.LOGFILE, level=logging.INFO,
		format="[%(levelname)s] %(asctime)s: %(message)s")

	run()