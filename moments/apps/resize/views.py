import Image, os

from moments     import settings
from django.http import HttpResponse

def resize_image_view(request):
	""" Resize and image via passed parameters. Note: we need a mod_rewrite rule or 
	requivalent to make sure we don't use Python to serve images more than required.
	FYI We could write some manage.py method to prime the cache. """
	try:
		width     = None
		height    = None
		file_type = None

		if "width" in request.GET:
			width = request.GET["width"]

		if "height" in request.GET:
			height = request.GET["height"]

		file_type        = "JPEG"
		file_path        = request.path
		file_path_chunks = file_path.split("/")
		file_name        = file_path_chunks[-1]
		path             = '/'.join(file_path_chunks[:-1])

		if width and not height:
			height = width

		if height and not width:
			width = height

		if width and height and file_type and file_name and file_path:
			dest_path = settings.PROJECT_BASE + path + "/" + width + "_" + height + "_" + file_name
			try:
				with open(dest_path) as f:
					return HttpResponse(open(dest_path), mimetype="image/jpeg")
			except:
				im = Image.open(settings.PROJECT_BASE + file_path)
				im.thumbnail((int(width),int(height)), Image.ANTIALIAS)
				im.save(dest_path, file_type)			
				return HttpResponse(open(dest_path), mimetype="image/jpeg")
	except:
		return HttpResponse("Error processing image", mimetype="text/html")	

	return HttpResponse("Not found", mimetype="text/html")	