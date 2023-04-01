# import base64

# class ProxyMiddleware(object):
    # def process_request(self, request, spider):
        # request.meta['proxy'] = "http://65.74.171.129:80"


import base64
from scrapy.http import Request
from scrapy.selector import Selector
import requests
from lxml import html
import json

class ProxyMiddleware(object):
	def process_request(self, request, spider):
		r = requests.get('http://gimmeproxy.com/api/getProxy')
		myobj = json.loads(r.content)
		myIPString = "http://" + str(myobj['ip']) + ":" + str(myobj['port'])
		request.meta['proxy'] = myIPString