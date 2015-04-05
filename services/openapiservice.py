#encoding:utf8
import json
import os
import time
import webbrowser
from clients import BaiduOpenApi, BaiduOpenApiException
from config import TOKENPATH

__all__ = [
	"apply_auth",
	"serialize_tokens",
	"deserialize_tokens",
	"refresh_tokens"
]

def apply_auth():
	"""
	Apply permissions to access user's baidu account.
	"""
	client = BaiduOpenApi()
	api = client.device.code
	resp = client.device.code.get(response_type="device_code", scope="netdisk")
	# open grant page and wait for user confirm
	webbrowser.open_new_tab(r"http://openapi.baidu.com/device?code=%s"%resp["user_code"])
	# yield to main
	yield
	# main will tell user to confirm and it will take a while
	# polling to wait server back
	return polling_tokens(resp["device_code"], resp["interval"], resp["expires_in"])

def polling_tokens(device_code, interval=5, expires_in=300):
	"""
	polling to wait server back
	return access_token, refresh_token
	"""
	begin = time.time()
	while(time.time() - begin < expires_in):
		# wait a while than ask server
		time.sleep(interval)
		client = BaiduOpenApi()
		try:
			resp = client.token.get(grant_type="device_token", code=device_code)
		except BaiduOpenApiException:
			continue
		# save tokens to harddisk
		return serialize_tokens(resp)
		# return tokens

def serialize_tokens(json_obj):
	"""
	save tokens to harddisk
	and return access_token, refresh_token
	"""
	# load into memory
	res = json.dumps(json_obj)
	with open(TOKENPATH, "w+") as f:
		f.write(res)
	return json_obj["access_token"], json_obj["refresh_token"]

def deserialize_tokens():
	"""
	return tokens load from disk
	return access_token, refresh_token
	"""
	if not os.path.isfile(TOKENPATH):
		return
	# if token exists
	with open(TOKENPATH, "r+") as f:
		context = f.read()
	try:
		res = eval(context)
		# load into memory
		return res["access_token"], res["refresh_token"]
	except:
		# unexcept token format
		pass

def refresh_tokens(refresh_token):
	"""
	refresh access token
	"""
	client = BaiduOpenApi()
	resp = client.token.get(grant_type="refresh_token", refresh_token=refresh_token)
	return serialize_tokens(resp)