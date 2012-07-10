"""
<iframe src="https://your_app_id.janraincapture.com/oauth/(signin|register)?
               response_type=code&
               redirect_uri=http%3A//www.example.com/oauth_redirect&
               client_id=your_client_id&
               xd_receiver=http%3A//www.example.com/xdcomm.html"></iframe>
"""
from functools import partial

from django import template


class JanrainCaptureNode(template.Node):
    def __init__(self, signin_or_register, app_id, client_id, domain):
        self.context = dict(
            signin_or_register=signin_or_register,
            app_id = app_id,
            client_id = client_id,
            domain = domain
        )

    def render(self, context):
        return """
        <iframe width="500px" height="500px" src="https://{app_id}.janraincapture.com/oauth/{signin_or_register}?response_type=code&redirect_uri=http://{domain}/janrain/oauth_redirect&client_id={client_id}&xdreceiver=http://{domain}/janrain/xdcomm.html"></iframe>
        """.format(**self.context)

def janrain_capture(signin_or_register, parser, token):
    if signin_or_register not in ('signin', 'register'):
        raise ValueError("you're probably doing this wrong, see janrain_capture_signin and janrain_capture_register")
    try:
        tag_name, app_id, client_id, domain = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('janrain_capture tag requires app_id, client_id, and domain arguments')

    return JanrainCaptureNode(signin_or_register, app_id, client_id, domain)

register = template.Library()
register.tag('janrain_capture_signin', partial(janrain_capture, 'signin'))
register.tag('janrain_capture_register', partial(janrain_capture, 'register'))
