"""
<iframe src="https://your_app_id.janraincapture.com/oauth/(signin|register)?
               response_type=code&
               redirect_uri=http%3A//www.example.com/oauth_redirect&
               client_id=your_client_id&
               xd_receiver=http%3A//www.example.com/xdcomm.html"></iframe>
"""
from functools import partial
import re

from django import template

# TODO surely a helper exists for this in Django
def literal_or_var(thing):
    """
    Given some string, return its value without quote delimiters or a
    Variable object representing the string. For example,

    a = self.literal_or_var('"hello"')
        a is 'hello'
    a = self.literal_or_var('hello')
        a is Variable('hello')

    :param thing: A string of the form "hello", 'hello', or hello
    :returns: either a Variable or a string
    """
    literal_re = '^[\'"].*[\'"]$'
    strip_quotes = lambda s: re.sub('[\'"]', '', s)

    if re.match(literal_re, thing):
        return strip_quotes(thing)
    else:
        return template.Variable(thing)

def maybe_resolve(context, thing):
    return thing.resolve(context) if type(thing) == template.Variable else thing

class JanrainCaptureNode(template.Node):
    def __init__(self, signin_or_register, app_id, client_id, domain):
        self.context = dict(
            signin_or_register=signin_or_register,
            app_id = literal_or_var(app_id),
            client_id = literal_or_var(client_id),
            domain = literal_or_var(domain),
        )

    def render(self, context):
        for key in ['app_id', 'client_id', 'domain']:
            self.context[key] = maybe_resolve(context, self.context[key])

        return """
        <iframe width="500px" height="1000px" src="https://{app_id}.janraincapture.com/oauth/{signin_or_register}?response_type=code&redirect_uri=http://{domain}/janrain/oauth_redirect&client_id={client_id}&xdreceiver=http://{domain}/janrain/xdcomm.html"></iframe>
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
