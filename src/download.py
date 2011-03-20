# -*- coding: utf-8 -*-

'''
Created on Jan 21, 2011

@author: krizan
'''
from base64 import encode
from data.model import Files
from google.appengine.ext import webapp
import base64
import logging

class DownloadFile(webapp.RequestHandler):
    def get(self, fileid):
        logging.info('downloading: ' + fileid)
        fileid = str(fileid).strip()
        if fileid and fileid != '':
            file = Files.get(fileid)
            if file:
                self.response.headers['Content-Type'] = 'application/octet-stream'
                self.response.headers['Content-Disposition'] = 'attachment; filename="' + file.name + '"'
                self.response.out.write(file.content)
