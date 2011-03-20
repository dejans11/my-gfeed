# -*- coding: utf-8 -*-

'''
Created on Jan 10, 2011

@author: dejans
'''

from data.model import Email, Files
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from utilities.util import TemplateHandler
import logging

class MailDetailsPage(TemplateHandler):

    @login_required
    def get(self, email_id):
        logging.info('MailDetailsPage processing')
        logging.info('email_id: ' + email_id)
        email_id = str(email_id).strip()
        if email_id and email_id != '':
            logging.info('valid email_id')
        
        user = users.get_current_user()
        
        email = Email.get(email_id)
        if email:
            logging.info('attachments')
            email._files = None
            if email.attachments:
                if len(email.attachments) > 0:
                    email._files = []
                for i in range(len(email.attachments)):
                    file = Files.get(email.attachments[i])
                    email._files.append(file)
                    logging.info('file.name : ' + file.name)

        template_values = {
                           'home_url' : '/home',
                           'email_url' : '/mail',
                           'nickname' : user.nickname(),
                           'logout_url': users.create_logout_url("/"),
                           'email': email
                }
        
        self.template_values = template_values
        self.render('mail_details.html')

