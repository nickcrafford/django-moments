from django.conf.urls        import patterns, include, url
from tastypie.api            import Api
from moments.apps.base.api   import MomentResource, EventResource
from moments.apps.base.views import single_page_view
from moments.apps.resize.views import resize_image_view
from django.contrib          import admin

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(MomentResource())
v1_api.register(EventResource())

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^api/',      include(v1_api.urls)),
    (r'^assets/',   resize_image_view),
    (r'^/?$',       single_page_view),
)
