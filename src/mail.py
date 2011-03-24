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
        
        page = self.request.get("page", default_value="1");
        page = int(page);
        
        q = RegisteredUserSettings.all()
        q.filter('user', user)
        user_settings_list = q.fetch(1)

        if user_settings_list == None or len(user_settings_list) == 0:
            # settings not yet created - for old users
            logging.info("creating user settings...")
            user_settings = RegisteredUserSettings(paging_pager_count=settings.PAGE_SIZE, user=user)
            user_settings.put()
        else:
            logging.info("user settings already exist...")
            user_settings = user_settings_list[0]
            logging.info("user_settings_list[0] : " + str(user_settings.paging_pager_count))
        
        btn_delete = self.request.get("btn_delete", None)
        
        if btn_delete != None:
            logging.info("deleting emails...")
            
            delete_mail_ids = self.request.get("delete_mail_ids", allow_multiple=True, default_value=None)
            deleted_count = 0
            keys_to_delete = []
            if delete_mail_ids:
                #change this to use a list of keys and delete list and not one key at a time
                for delete_mail_id in delete_mail_ids:
                    logging.info("deleting email : " + str(delete_mail_id))
                    keys_to_delete.append(delete_mail_id)
                    #Email.delete(delete_mail_id)
                    deleted_count += 1

                db.delete(keys_to_delete)
                logging.info("deleted_count : " + str(deleted_count))
            
            if page > 1 and deleted_count == int(user_settings.paging_pager_count):
                page -= 1
        
        emails = Email.all()
        emails.filter('user', user).order('-received')

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
            emails_paged = PagedQuery(emails, int(user_settings.paging_pager_count))
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

