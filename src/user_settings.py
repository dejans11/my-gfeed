# -*- coding: utf-8 -*-

'''
Created on Jan 10, 2011

@author: dejans
'''

from data.model import RegisteredUserSettings
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from mako.template import Template as makotpl
from utilities.paging import *
from utilities.util import TemplateHandler
import logging
import os
import settings

#from util import login_required

class UserSettingsPage(TemplateHandler):

    @login_required
    def get(self):
        logging.info('UserSettingsPage processing')
        user = users.get_current_user()
        
        q = RegisteredUserSettings.all()
        q.filter('user', user)
        user_settings = q.fetch(1)
        #query = db.GqlQuery('select * from Email where user = :user', user=user)
        #query.bind(user=user)
        #emails = db.Query(Email).filter('user', user)

        if user_settings == None or len(user_settings) == 0:
            # settings not yet created - for old users
            logging.info("creating user settings...")
            user_settings = RegisteredUserSettings(paging_pager_count=settings.PAGE_SIZE, user=user)
            user_settings.put()
        else:
            user_settings = user_settings[0]
        
        msg_updated = None
        
        btn_submit = self.request.get("btn_submit", None)
        
        if btn_submit != None:
            #update user settings
            logging.info("updating user settings...")
            
            paging_pager_count = int(self.request.get("paging_pager_count"))
            logging.info("paging_pager_count new value: " + str(paging_pager_count))
            
            user_settings.paging_pager_count = paging_pager_count
            user_settings.put()
            msg_updated = "Settings updated successfully..."

        self.template_values = {
                           'home_url' : '/home',
                           'nickname' : user.nickname(),
                           'logout_url' : users.create_logout_url("/"),
                           
                           'msg_updated' : msg_updated,
                           'user_settings' : user_settings
                }

        self.render('user_settings.html')

