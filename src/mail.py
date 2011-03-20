# -*- coding: utf-8 -*-

'''
Created on Jan 10, 2011

@author: dejans
'''

from data.model import Email, RegisteredUserSettings
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from mako.template import Template as makotpl
from utilities.paging import *
from utilities.util import TemplateHandler
import logging
import os
import settings

class MailPage(TemplateHandler):

    @login_required
    def get(self):
        logging.info('MailPage processing')
        user = users.get_current_user()
        
        q = RegisteredUserSettings.all()
        q.filter('user', user)
        user_settings_list = q.fetch(1)

        if user_settings_list == None or len(user_settings_list) == 0:
            # settings not yet created - for old users
            logging.info("creating user settings...")
            user_settings = RegisteredUserSettings(paging_pager_count=settings.PAGE_SIZE, user=user)
            user_settings.put()
        else:
            user_settings = user_settings_list[0]
        
        emails = Email.all()
        emails.filter('user', user).order('-received')
        
        page = self.request.get("page", default_value="1");
        page = int(page);
        emails_paged = self.emails_paged(emails, page, user_settings)
        
        emails = emails_paged["results"];
        next_page = None;
        prev_page = None;
        if emails_paged["nextPageExists"]: next_page = page + 1;
        if emails_paged["prevPageExists"]: prev_page = page - 1;

        template_values = {
                           'home_url' : '/home',
                           'nickname' : user.nickname(),
                           'logout_url': users.create_logout_url("/"),
                           'emails': emails,
                           'next_page': next_page,
                           'prev_page': prev_page,
                           'user_settings': user_settings
                }

        self.template_values = template_values
        self.render('mail.html')

    def emails_paged(self, emails, page, user_settings):
        ret = {};
        if emails is not None:
            emails_paged = PagedQuery(emails, settings.PAGE_SIZE)
            if page > 1:
                ret["results"] = emails_paged.fetch_page(page);
            else:
                ret["results"] = emails_paged.fetch_page();
            ret["nextPageExists"] = emails_paged.has_page(page + 1);
            if page - 1 > 0:
                ret["prevPageExists"] = emails_paged.has_page(page - 1);
            else:
                ret["prevPageExists"] = False;
        else:
            ret["results"] = []
        return ret;

