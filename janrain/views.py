from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from janrain.api import JanrainClient

from django.views.generic import View, TemplateView

class JanrainView(View):
    """
        Sets up the non-cacheability of all views subclassed from here. They
        all work with sessions and request/response objects and should never be
        allowed to stay in a cache.
    """
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(JanrainView, self).dispatch(*args, **kwargs)


class JanrainOauthRedirectView(JanrainView):
    """
        The ``redirect_uri`` used with the Capture API.  Accepts a ``code``
        parameter in GET that is exchanged for an access_token. With the access
        token we can then read/update the authenticated user's information.
        Takes care of authenticating/logging in user.
    """
    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        try:
            code = request.REQUEST['code']
        except KeyError:
            return HttpResponseRedirect('/')

        api_key = settings.JANRAIN_API_KEY
        client_id = settings.JANRAIN_CAPTURE_CLIENT_ID
        client_secret = settings.JANRAIN_CAPTURE_CLIENT_SECRET
        redirect_uri = settings.JANRAIN_CAPTURE_REDIRECT_URI
        app_id = settings.JANRAIN_CAPTURE_APP_ID

        api_url = 'https://%s.janraincapture.com/' % app_id
        client = JanrainClient(api_key, endpoint=api_url)

        response = client.oauth_token(
            code=code,
            redirect_uri=redirect_uri,
            grant_type='authorization_code',
            client_id=client_id,
            client_secret=client_secret,
        )

        if not response or 'error' in response:
            return HttpResponseRedirect('/')

        try:
            access_token = response['access_token']
        except KeyError:
            return HttpResponseRedirect('/')

        response = client.entity(access_token=access_token)

        if not response.get('stat') == 'ok':
            return HttpResponseRedirect('/')

        user_data = response['result']

        user = auth.authenticate(user_data=user_data)
        request.user = user
        auth.login(request, user)

        return HttpResponseRedirect(request.GET.get('redirect_to', '/'))


class JanrainLoginView(JanrainView):
    """
        Redirect URL for Engage. Looks for ``token`` parameter in ``POST`` that
        is used to request profile information for the authenticating user.
        Takes care of authenticating/logging in user.
    """
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            token = request.POST['token']
        except KeyError:
            return HttpResponseRedirect('/')

        api_key = settings.JANRAIN_API_KEY
        api_url = getattr(settings, 'JANRAIN_API_URL', 'https://rpxnow.com/api/v2/')
        client = JanrainClient(api_key, endpoint=api_url)

        auth_info = client.auth_info(token)

        if not auth_info['stat'] == 'ok':
            return HttpResponseRedirect('/')

        user = auth.authenticate(auth_info=auth_info)

        request.user = user
        auth.login(request, user)

        return HttpResponseRedirect(request.GET.get('redirect_to', '/'))


class JanrainLogoutView(JanrainView):
    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return HttpResponseRedirect(request.GET.get('redirect_to', '/'))


class JanrainLoginPageView(JanrainView):
    def get(self, request, *args, **kwargs):
        context = {'next':request.GET['next']}
        return render_to_response(
            'janrain/loginpage.html',
            context,
            context_instance=RequestContext(request)
        )


class JanrainXDCommView(TemplateView):
    template_name='xdcomm.html'
