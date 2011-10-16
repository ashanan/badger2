from django.conf.urls.defaults import *

from django.conf import settings

urlpatterns = patterns('profiles.views',
    url(r'^home/?$', 'home', name='profiles.home'),
    url(r'^profile/(?P<username>[^/]+)/?$', 'profile_view',
        name='profiles.profile_view'),
    url(r'^profile/(?P<username>[^/]+)/edit/?$', 'profile_edit',
        name='profiles.profile_edit'),
)
