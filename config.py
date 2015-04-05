#encoding:utf8
import os

# input your api key here
BAIDU_API_KEY = "4OySt4LBqrR6QNyo7yXywsnC"#os.environ["BAIDU_API_KEY"]
BAIDU_SECRET_KEY = "GQhhC485PAejjST6HiAPbG0kTCSlrxWW"#os.environ["BAIDU_SECRET_KEY"]
# name of your app
APPNAME = "TSGUploader"
# path to store your token
TOKENPATH = os.path.join(os.getcwd(), r"authorization.json")
# baiduyun path prefix
PATHPREFIX = "/apps" + '/' + APPNAME.lower()
# max simple upload size (bytes)
PIECE = 1024*1024