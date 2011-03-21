# -*- coding: utf-8 -*-

'''
Created on Jan 21, 2011

@author: krizan
'''
from StringIO import StringIO
from base64 import encode
from data.model import Files, Email
from google.appengine.ext import webapp
import base64
import logging
import zipfile

class DownloadZipFile(webapp.RequestHandler):
    def get(self, emailid):
        logging.info('downloading zip file for email: ' + emailid)
        emailid = str(emailid).strip()
        if emailid and emailid != '':
            email = Email.get(emailid)
            if email:
                logging.info('email attachments count: ' + str(len(email.attachments)))
                
                # create the zip stream
                zipstream=StringIO()
                zfile = zipfile.ZipFile(zipstream,"w")

                for attachment in email.attachments:
                    file_attachment = Files.get(attachment)
                    if file_attachment:
                        zfile = self.addFile(zfile, file_attachment.name.decode('utf-8'), file_attachment.content.decode('utf-8'))
                
                self.response.headers['Content-Type'] = 'application/zip'
                self.response.headers['Content-Disposition'] = 'attachment; filename="attachments.zip"'
                self.response.out.write(zfile.content)
            
    def addFile(self, zipstream, fname, content):
        # store the contents in a stream
        f = StringIO(content)
        f.seek(0)
        # write the contents to the zip file
        zipstream.writestr(fname, content)
