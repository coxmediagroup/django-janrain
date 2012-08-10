from django.conf.urls.defaults import patterns, url
from janrain.views import JanrainLoginView, JanrainLogoutView, JanrainLoginPageView, JanrainOauthRedirectView, JanrainReturnView, JanrainXDCommView

urlpatterns = patterns('',
    url(r'^login/$', JanrainLoginView.as_view(), name='login'),
    url(r'^logout/$', JanrainLogoutView.as_view(), name='logout'),
    url(r'^loginpage/$', JanrainLoginPageView.as_view(), name='loginpage'),
    url(r'^xdcomm.html$', JanrainXDCommView.as_view(), name='xdcomm'),
    url(r'^return.html$', JanrainReturnView.as_view(), name='return'),
    url(r'^oauth_redirect$', JanrainOauthRedirectView.as_view(), name='oauth_redirect'),
)
