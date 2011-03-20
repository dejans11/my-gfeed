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

#from util import login_required

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
                    #logging.info('email[' + unicode(i+1) + '] : [' + unicode(email.attachments[i]) + ']')
                    #file_key = db.Key.from_path('Files', email.attachments[i])
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
        #path = os.path.join(os.path.dirname(__file__), 'html/mail.html')
        #mako_template = makotpl(filename=path, default_filters=['decode.utf8'])
        #self.response.out.write(mako_template.render_unicode(**template_values))
        
        self.template_values = template_values
        self.render('mail_details.html')

