from django.contrib           import admin
from django.contrib.admin     import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.conf.urls         import patterns
from moments.apps.base.views  import admin_batch_load_view
from moments.apps.base.models import Moment, Event
from adminsortable.admin      import SortableAdminMixin
from tastypie.models          import ApiKey

# Custom Filters

class CaptionFilter(SimpleListFilter):
	title          = _('has caption')
	parameter_name = 'has_caption'

	def lookups(self, request, model_admin):
		return (
			(1, _('Yes')),
			(0, _('No')),
		)

	def queryset(self, request, queryset):
		if self.value() == '0':
			return queryset.filter(caption="")
		if self.value() == '1':
			return queryset.exclude(caption="")
		return queryset

# Custom Actions

def publish_action(modeladmin, request, queryset):
	queryset.update(published=True)

publish_action.short_description = "Mark selected Moments as published"

def un_publish_action(modeladmin, request, queryset):
	queryset.update(published=False)

un_publish_action.short_description = "Mark selected Moments as un-published"

def save_inlines_action(modeladmin, request, queryset):
	for item in queryset:
		id = str(item.id)
		moment = Moment.objects.get(id=id)
		moment.caption = request.POST["caption_input_" + id]
		try:
			moment.event = Event.objects.get(id=request.POST["event_select_"  + id])
		except:
			moment.event = None
		
		moment.save()

save_inlines_action.short_description = 'Save caption and "Event" updates for selected Moments'


def propogate_event_to_all_action(modeladmin, request, queryset):
	first = None
	for item in queryset:
		first = item
		break

	try:
		queryset.update(event=Event.objects.get(id=request.POST["event_select_" + str(first.id)]))
	except:
		queryset.update(event=None)

propogate_event_to_all_action.short_description = 'Propagate first selected Moment\'s "Event" to ALL selected Moments'

# Triggers	

def create_update_trigger(request, obj):
	try:
		obj.create_user
	except:
		obj.create_user = request.user
	obj.update_user = request.user
	obj.save()	

# Admin Models      

class EventAdmin(SortableAdminMixin, admin.ModelAdmin):
	list_display  = ('title', 'published',)
	list_filter   = ['published',]	
	search_fields = ['title', 'description']
	actions       = [publish_action, un_publish_action]

	def save_model(self, request, obj, form, change): 
		create_update_trigger(request, obj)

class MomentAdmin(admin.ModelAdmin):
	list_display  = ('create_date', 'photographer','published', 'event_select', 'image_preview', 'caption_input',)
	list_filter   = ['published', 'photographer', 'event', CaptionFilter]
	search_fields = ['caption']
	list_per_page = 10
	actions       = [publish_action, un_publish_action, save_inlines_action, propogate_event_to_all_action]

	class Media:
		js  = ('/static/js/moments_admin.js', )
		css = {'all' : ('/static/css/moments_admin.css',)}

	def caption_input(self, obj):
		return u'<textarea maxlength="150"  tabindex="1" class="moment_caption_input moment_caption_input_%s" name="caption_input_%s">%s</textarea>' % (obj.rotate_angle, str(obj.id), obj.caption)

	caption_input.short_description = "Caption"
	caption_input.allow_tags        = True

	def event_select(self, obj):
		events    = Event.objects.filter(published=True)
		list_html = []
		for event in events:
			if event == obj.event:
				select_text = "selected"
			else:
				select_text = ""
			list_html.append(u'<option %s value="%s">%s</option>' % (select_text, event.id, event.title))
		return u'<select name="event_select_%s"><option value="">Select an event</option>%s</select>' % (str(obj.id), u''.join(list_html))

	event_select.short_description = "Event"
	event_select.allow_tags        = True		

	def image_preview(self, obj):
		if obj.image:
			return u'<div class="moment_image_cont_%s"><img class="moment_image_preview moment_image_rotate_%s" src="/assets/%s?width=125" /></div>' % (obj.rotate_angle,obj.rotate_angle, str(obj.image))
		else:
			return '(No Image)'
	
	image_preview.short_description = 'Preview'
	image_preview.allow_tags        = True		

	def save_model(self, request, obj, form, change):
		""" Call any triggers when saving the model. """
		create_update_trigger(request, obj)


	def admin_batch_load_view(self, request):
		""" Wrapper for the batch load view. """
		return admin_batch_load_view(request, self)

	def get_urls(self):
		""" Add custom URLs to the admin page for Moment. """
		urls   = super(MomentAdmin, self).get_urls()
		t_urls = patterns('', (r'^upload-zip/$', self.admin_batch_load_view))
		return t_urls + urls

admin.site.register(Moment, MomentAdmin)
admin.site.register(Event,  EventAdmin)
admin.site.unregister(ApiKey)

