from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator

from janrain.api import JanrainClient

from django.views.generic import View, TemplateView

class JanrainView(View):
    pass

class JanrainLoginView(JanrainView):
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
    template_name='janrain/xdcomm.html'
