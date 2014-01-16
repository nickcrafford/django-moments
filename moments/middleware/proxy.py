import re

from moments                       import settings
from django.views.decorators.cache import patch_cache_control
from django.http                   import HttpResponse
from django.core.cache             import cache

class CacheControlProxy(object):
	""" Simple Cache Control Proxy middleware. """
	def process_response(self, request, response):
		for pair in settings.CACHE_CONTROL:
			if re.search(pair[0], request.path):
				response['Cache-Control'] = ""
				patch_cache_control(response, **pair[1])
				break
		return response

class ReverseProxy(object):
	def process_request(self, request):
		for pair in settings.REVERSE_PROXY_RULES:
			if re.search(pair[0], request.path):
				args = cache.get(request.path + "_" + str(request.GET))
				if args:
					resp = HttpResponse(**args)
					resp["ReverseProxy"] = "HIT"
					return resp
		return None

	def process_response(self, request, response):
		for pair in settings.REVERSE_PROXY_RULES:
			if re.search(pair[0], request.path):
				cache.add(request.path + "_" + str(request.GET), {"content" : response.content, "mimetype" : pair[2]}, pair[1])
		return response