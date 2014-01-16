import datetime, os

from django.db                     import models
from django.contrib.auth.models    import User
from moments                       import settings
from taggit.managers               import TaggableManager
from django_resized                import ResizedImageField
from django.core.cache             import cache

ROTATION_ANGLES = (
	('-180', '-180 degrees'),
	('-90',  '-90 degrees'),
	('0',    '0 degrees'),
	('90',   '90 degrees'),
	('180',  '180 degrees'),
)

class Base(models.Model):
	create_user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_create_user',editable = False)
	update_user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_update_user',editable = False)
	create_date = models.DateTimeField(auto_now_add=True,editable = False)	
	update_date = models.DateTimeField(auto_now=True,editable = False)

	class Meta:
		abstract = True

	def save(self):
		""" Clear the API and image resize cache on all model saves. """
		super(Base,self).save()
		cache.clear()

class Event(Base):
	""" An event i.e. Christmas 2013. """
	published     = models.BooleanField()
	title         = models.CharField(max_length=250, unique=True)
	display_order = models.IntegerField()

	def __str__(self):
		return self.title

	class Meta:
		verbose_name        = "Event"
		verbose_name_plural = "Events"	
		ordering            = ('display_order',)

class Moment(Base):
	""" A snapshot or video of a precious moment. """
	published      = models.BooleanField()
	photographer   = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_author')
	event          = models.ForeignKey(Event, null=True, blank=True)
	image          = ResizedImageField(max_width=1440, max_height=900,upload_to=settings.MOMENT_UPLOAD_PATH)
	rotate_angle   = models.CharField(max_length=150,choices=ROTATION_ANGLES,default='0')
	caption        = models.CharField(max_length=150, blank=True, null=True)
	tags           = TaggableManager(blank=True)

	def __str__(self):
		return self.caption

	class Meta:
		verbose_name        = "Moment"
		verbose_name_plural = "Moments"
		ordering            = ('-create_date',)