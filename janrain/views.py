from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext

from janrain.api import JanrainClient

@csrf_exempt
def login(request):
    try:
        token = request.POST['token']
    except KeyError:
        return HttpResponseRedirect('/')

    api_key = settings.JANRAIN_API_KEY
    api_url = settings.get('JANRAIN_API_URL', 'https://rpxnow.com/api/v2')
    client = JanrainClient(api_key, endpoint=api_url)

    auth_info = client.auth_info(token)

    if not auth_info['stat'] == 'ok':
        return HttpResponseRedirect('/')

    user = auth.authenticate(auth_info)

    request.user = user
    auth.login(request, user)

    return HttpResponseRedirect(request.GET.get('redirect_to', '/'))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.GET.get('redirect_to', '/'))

def loginpage(request):
    context = {'next':request.GET['next']}
    return render_to_response(
        'janrain/loginpage.html',
        context,
        context_instance=RequestContext(request)
    )
