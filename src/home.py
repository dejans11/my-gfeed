# -*- coding: utf-8 -*-

'''
Created on Jan 11, 2011

@author: dejans
'''

from data.model import RegisteredUser
from google.appengine.api import memcache, users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from mako.template import Template as makotpl
from utilities.util import check_user_registered, TemplateHandler
import logging
import os

#from util import login_required

class HomePage(TemplateHandler):

    @login_required
    def get(self):
        user = users.get_current_user()
        logging.info('HomePage processing for [%(email)s].' % { 'email' : user.email()})
        
        #registered_user = RegisteredUser.all()
        #registered_user.filter('user', user)
        
        if check_user_registered(user) == False :
            registered_user = RegisteredUser()
            registered_user.user = user
            registered_user.put()
            logging.info('User registered for the first time.')

        template_values = {
                           'nickname' : user.nickname(),
                           'email_url' : '/mail',
                           'logout_url': users.create_logout_url("/"),
                           'settings_url' : '/settings'
        }
        
        confirmation_code = memcache.get(user.email())
        if confirmation_code is not None:
            template_values['confirmation_code'] = confirmation_code
        
        #path = os.path.join(os.path.dirname(__file__), 'html/homepage.html')
        #mako_template = makotpl(filename=path, default_filters=['decode.utf8'])
        #self.response.out.write(mako_template.render_unicode(**template_values))
        self.template_values = template_values
        self.render('homepage.html')
        
