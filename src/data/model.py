# -*- coding: utf-8 -*-

'''
Created on Jan 9, 2011

@author: dejans
'''

from google.appengine.ext import db

class Files(db.Model):
    name = db.StringProperty(required=True)
    content = db.BlobProperty()

class Email(db.Model):
    '''
    classdocs
    '''
    user = db.UserProperty()
    
    sender = db.StringProperty(required=True)
    to = db.StringProperty(required=True)
    cc = db.TextProperty(required=False)
    bcc = db.TextProperty(required=False)
    reply_to = db.StringProperty(required=False)
    subject = db.StringProperty(required=False, multiline=True)
    body = db.TextProperty(required=False)
    html = db.TextProperty(required=False)
    
    attachments = db.ListProperty(item_type=db.Key)
    _files = None
    
    received = db.DateTimeProperty(auto_now_add=True)

class RegisteredUser(db.Model):
    user = db.UserProperty()
    registered = db.DateTimeProperty(auto_now_add=True)

class RegisteredUserSettings(db.Model):
    user = db.UserProperty()
    last_changed = db.DateTimeProperty(auto_now=True)
    
    paging_pager_count =db.IntegerProperty(required=True) 

class DBLogging(db.Model):
    name = db.StringProperty(required=True)
    value = db.StringProperty(required=True)
    date_time = db.DateTimeProperty(auto_now_add=True)