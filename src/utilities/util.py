# -*- coding: utf-8 -*-

'''
Created on Jan 11, 2011

@author: krizan
'''

from data.model import RegisteredUser
from google.appengine.api.users import User
from google.appengine.ext import webapp
from mako.lookup import TemplateLookup
import logging
#from google.appengine.api import users
#from mako.template import Template as makotpl
#import os


#def login_required(func):
#    def wrapper(self, *args, **kw):
#        user = users.get_current_user()
#        if not user:
#            logging.info('Unathorized access...')
#            template_values = {
#                           'login_url' : users.create_login_url(self.request.uri)
#                           }
#            path = os.path.join(os.path.dirname(__file__), 'authorized.html')
#            path = 'html/authorized.html'
#            mako_template = makotpl(filename=path, default_filters=['decode.utf8'])
#            self.response.out.write(mako_template.render_unicode(**template_values))
#        else:
#            logging.info('Athorized access...')
#            return func(self, *args, **kw)
#        return wrapper

def check_user_registered(user):
        registered = False
        
        registered_user = RegisteredUser.all()
        registered_user.filter('user', user)
        
        if registered_user.count(1) == 1:
            logging.info('User already registered.')
            registered = True
        elif registered_user.count() > 1:
            logging.info('DB corrupted. User registered more than once.')

        return registered
    
def check_user_registered_by_email(email):
        registered = None
        
        registered_user = RegisteredUser.all()
        
        registered_user.filter('user', User(email))
        
        if registered_user.count(1) == 1:
            logging.info('check_user_registered_by_email User already registered.')
            registered = registered_user.get().user
        elif registered_user.count() > 1:
            logging.info('DB corrupted. User registered more than once.')
        else:
            logging.info('User not registered')

        return registered

def parse_email(email):
    if '<'  in email>= 0:
        email = email[email.index("<") + 1:]
        email = email[:email.index(">")]
    return email

class TemplateHandler(webapp.RequestHandler): 
    """Base class for handlers using templates. Handles setting up 
    template search paths, and passing the context to the template. 
    Subclasses should call 'self.render(template_name)'. 
    """ 
    def __init__(self, **kwargs): 
        """Setup the context that will be passed to the template.""" 
        webapp.RequestHandler.__init__(self, **kwargs) 
        self.template_values = {} 
    def render(self, template_name, values_dict=None): 
        """Setup search paths, and render the template. 
        Any values passed in will be combined with 
        self.template_values, and passed to the template. 
        """ 
        directories = ['/html', 'html'] 
        # Simple example of using the user-agent to set the search paths. 
#        ua = self.request.headers.get('user_agent').lower() 
#        if "mobile" in ua and "webkit" in ua: 
#            directories.insert(0, 'templates/mobile/webkit') 
            
        lookup = TemplateLookup(directories=directories, output_encoding='utf-8') 
        template = lookup.get_template(template_name) 
        if values_dict: 
            self.template_values.update(values_dict) 
        self.response.out.write(template.render(**self.template_values))