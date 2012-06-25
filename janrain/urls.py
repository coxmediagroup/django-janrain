from django.conf.urls.defaults import patterns, url
from janrain.views import JanrainLoginView, JanrainLogoutView, JanrainLoginPageView, JanrainXDCommView

urlpatterns = patterns('',
    url(r'^login/$', JanrainLoginView.as_view(), name='login'),
    url(r'^logout/$', JanrainLogoutView.as_view(), name='logout'),
    url(r'^loginpage/$', JanrainLoginPageView, name='loginpage'),
    url(r'^xdcomm.html$', JanrainXDCommView, name='xdcomm'),
)
