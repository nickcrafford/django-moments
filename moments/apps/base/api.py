import Image, StringIO

from tastypie.resources       import ModelResource
from moments.apps.base.models import Event, Moment
from tastypie                 import fields
from django.db                import models
from taggit.models            import Tag
from moments                  import settings

def create_data_uri(obj, image_attrib_name, image_width, image_height):
	""" Thumbnail an image and convert it to a data uri for adding to a tastypie bundle. """
	output = StringIO.StringIO()
	image  = Image.open(settings.MEDIA_ROOT + str(getattr(obj, image_attrib_name)))
	
	image.thumbnail((int(image_width),int(image_width)), Image.ANTIALIAS)		
	image.save(output, "JPEG", transparency=0)

	contents = output.getvalue().encode("base64")
	output.close()	
	return "data:image/jpg;base64," + contents

class TagResource(ModelResource):
	class Meta:
		queryset        = Tag.objects.all()		
		allowed_methods = ['get']

class EventResource(ModelResource):
	class Meta:
		queryset        = Event.objects.filter(published=True)
		resource_name   = 'event'
		allowed_methods = ['get']
		ordering        = ['display_order']

class MomentResource(ModelResource):
	event = fields.ToOneField(EventResource, 'event', full=True, null=True)
	tags  = fields.ToManyField(TagResource, 'tags', full=True, null=True)	
	class Meta:
		queryset        = Moment.objects.filter(published=True).exclude(event=None)
		resource_name   = 'moment'
		allowed_methods = ['get']
		ordering        = ['create_date', 'id', 'event']

	def alter_list_data_to_serialize(self, request, to_be_serialized):
		""" Add a data uri for the image attached to the Moment being served. """
		for bundle in to_be_serialized['objects']:
			obj = bundle.obj
			bundle.data["data_uri"] = create_data_uri(obj, "image", settings.MOMENT_API_THUMB_WIDTH, settings.MOMENT_API_THUMB_WIDTH)
		return to_be_serialized