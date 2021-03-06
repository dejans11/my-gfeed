# -*- coding: utf-8 -*-

'''
Created on Jan 9, 2011

@author: dejans
'''
import logging
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache
from data.model import Email, Files
import settings
from utilities.util import check_user_registered_by_email, parse_email
import datetime
from google.appengine.api import taskqueue

class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + str(mail_message.sender))

        to_email_parsed = str(mail_message.to)
        to_email_parsed = parse_email(to_email_parsed)
        
        logging.info("to email trimmed: " + to_email_parsed)

        user = check_user_registered_by_email(to_email_parsed)

        html_body = ''
        plain_body = ''

        bodies = mail_message.bodies()
        for content_type, body in bodies:
            if body.encoding == '8bit':
                body.encoding = '7bit'
        
            #test for html content
            if content_type == "text/html":
                #parse html result
                html_body += body.decode()
                logging.info('body text/html')
            
            if content_type == "text/plain":
                plain_body += body.decode()
                logging.info('body text/plain')

        from_email_parsed = mail_message.sender
        from_email_parsed = parse_email(from_email_parsed)
        if from_email_parsed == 'mail-noreply@google.com':
            self.check_if_confirmation_mail(plain_body, html_body)

        if not user:
            logging.info('check_user_registered_by_email is FALSE; from : ' + from_email_parsed)
        else:
            logging.info('check_user_registered_by_email is TRUE')

            params = {}
            if hasattr(mail_message, 'sender'):
                params['sender'] = mail_message.sender
            if hasattr(mail_message, 'to'):
                params['to'] = mail_message.to
            if hasattr(mail_message, 'cc'):
                params['cc'] = mail_message.cc
            if hasattr(mail_message, 'bcc'):
                params['bcc'] = mail_message.bcc
            if hasattr(mail_message, 'reply_to'):
                params['reply_to'] = mail_message.reply_to
            if hasattr(mail_message, 'subject'):
                params['subject'] = mail_message.subject
            if hasattr(mail_message, 'body'):
                params['body'] = plain_body
            if hasattr(mail_message, 'html'):
                params['html'] = html_body
            
            params['user'] = user
            
            attachments = []
            if hasattr(mail_message, 'attachments'):
                for (name, content) in mail_message.attachments:
                    logging.info('new attachment name : ' + name)
                    try:
                        new_file = Files(name=name, content=db.Blob(content.decode()))
                        attachments.append(new_file)
                        #new_file.put()
                        #attachments.append(new_file.key())
                    except:
                        logging.info('decoding content failed')                        
                #if len(attachments) <> 0:
                    #params['attachments'] = attachments
            
            new_email = Email(**params)
            
            #try:
                #new_email.put()
            #except:
                #logging.info('html_body: ' + html_body)
                #logging.info('plain_body: ' + plain_body)
                
            mem_key = datetime.datetime.now()
            mem_key = str(mem_key.year) + str(mem_key.month) + str(mem_key.day) + str(mem_key.hour) + str(mem_key.minute) + str(mem_key.second) + str(mem_key.microsecond)
            memcache.add(key=mem_key, value={ 'email' : new_email, 'files' : attachments})
            taskqueue.add(url='/task_put_email', params={'mem_key': mem_key})
            
            logging.info('new email mem_key : ' + str(mem_key))
        
    def check_if_confirmation_mail(self, html_body, plain_body):
        email = None
        confirmation_code_html = None
        confirmation_code_plain = None
        search_string = 'Confirmation code: '
        
        if not html_body:
            html_body = ''
        else:
            strings = html_body.split(' ')
            if len(strings) > 0:
                email = strings[0];
        if 'all@my-gfeed.appspotmail.com' in html_body:
            index = str(html_body).find(search_string)
            if index != -1:
                index += len(search_string)
                confirmation_code_html = html_body[index:index + 10].strip()
        
        if not plain_body:
            plain_body = ''
        else:
            strings = plain_body.split(' ')
            if len(strings) > 0:
                email = strings[0];
        if 'all@my-gfeed.appspotmail.com' in plain_body:
            index = str(plain_body).find(search_string)
            if index != -1:
                index += len(search_string)
                confirmation_code_plain = plain_body[index:index + 10].strip()
        
        if confirmation_code_html:
            #keep in memory for 5 minutes
            memcache.add(key=email, value=confirmation_code_html, time=300)
        elif confirmation_code_plain:
            memcache.add(key=email, value=confirmation_code_plain, time=300)
        
        logging.info('email : [' + str(email) + ']')
        logging.info('confirmation_code_html : [' + str(confirmation_code_html) + ']')
        logging.info('confirmation_code_plain : [' + str(confirmation_code_plain) + ']')
        
        #all@my-gfeed.appspotmail.com.
        #Confirmation code: 45304100

application = webapp.WSGIApplication(
                                     [EmailHandler.mapping()],
                                     debug=settings.DEBUG)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

