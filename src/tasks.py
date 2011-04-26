# -*- coding: utf-8 -*-

'''
Created on Apr 26, 2011

@author: krizan
'''
from google.appengine.ext import webapp
import logging
from google.appengine.api import memcache

class TaskEmailPut(webapp.RequestHandler):
    def post(self):
        
        logging.info('processing TaskEmailPut')
        
        mem_key = self.request.get('mem_key')
        mem_key_valid = False
        try:
            email_data = memcache.get(mem_key)
            files = email_data['files']
            email = email_data['email']
            mem_key_valid = True
        except:
            logging.info("failed getting converting mem_key to long :" + mem_key)
        
        if mem_key_valid:
            attachments = []
            for file in files:
                logging.info('new files name : ' + file.name)
                try:
                    file.put()
                    attachments.append(file.key())
                except:
                    logging.info('decoding content failed')
                
            if len(attachments) <> 0:
                    email.attachments = attachments
            
            try:
                email.put()
            except:
                logging.info('html_body: ' + email.html)
                logging.info('plain_body: ' + email.body)
        