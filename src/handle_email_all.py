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
#from google.appengine.api.memcache import Client 
from data.model import Email, Files, DBLogging
import settings
from utilities.util import check_user_registered_by_email, parse_email

class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + str(mail_message.sender) + " ; message to : " + str(mail_message.to))

        to_email_parsed = str(mail_message.to)
        to_email_parsed = parse_email(to_email_parsed)
        
        logging.info("to email trimmed: " + to_email_parsed)

        #is_registered = RegisteredUser.gql('where user=:1', users.get_current_user())
        user = check_user_registered_by_email(to_email_parsed)

        html_body = ''
        plain_body = ''
        
        html_bodies = mail_message.bodies('text/html')
        for content_type, bodies in html_bodies:
            try:
                html_body += unicode(bodies.decode())
            except:
                logging.info('html_body bodies.decode() failed for content_type : ' + content_type)
                logging.info('html_body bodies.decode() failed for bodies : ' + str(bodies))
        
        if len(html_body) == 0:
            plaintext_bodies = mail_message.bodies('text/plain')
            for content_type, bodies in plaintext_bodies:
                try:
                    plain_body += unicode(bodies.decode())
                except:
                    logging.info('plain_body bodies.decode() failed for content_type : ' + content_type)
                    logging.info('plain_body bodies.decode() failed for bodies : ' + str(bodies))
        
        #DBLogging
        #plain_body = ''
        #html_body = ''
        #if hasattr(mail_message, 'body'):
            #plain_body = unicode(mail_message.body.decode())
            #plain_body = mail_message.body
        #if hasattr(mail_message, 'html'):
            #html_body = unicode(mail_message.html.decode())
            #html_body = mail_message.html

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
            
            if hasattr(mail_message, 'attachments'):
                attachments = []
                for (name, content) in mail_message.attachments:
                    logging.info('new attachment name : ' + name)
                    try:
                        new_file = Files(name=name, content=db.Blob(content.decode()))
                        new_file.put()
                        attachments.append(new_file.key())
                    except:
                        logging.info('decoding content failed')                        
                if len(attachments) <> 0:
                    #attachments = None
                    params['attachments'] = attachments
            
            new_email = Email(**params)
            new_email.put()
        
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

