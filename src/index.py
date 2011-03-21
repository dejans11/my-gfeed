# -*- coding: utf-8 -*-

from download import DownloadFile
from download_zip import DownloadZipFile
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from home import HomePage
from mail import MailPage
from mail_details import MailDetailsPage
from mako.template import Template as makotpl
from user_settings import UserSettingsPage
from utilities.util import TemplateHandler
import logging
import os
import settings



class IndexPage(TemplateHandler):
    def get(self):
        
        user = users.get_current_user()
        if user:
            logging.info('Αlready signed in: redirect to home [%(email)s].' % { 'email' : user.email()})
            self.redirect('/home')
        
        template_values = {
                           'login_url' : users.create_login_url('/')
                           }

        self.template_values = template_values
        self.render('index.html')

application = webapp.WSGIApplication(
                                     [('/', IndexPage),
                                      ('/home', HomePage),
                                      (r'/download/(.*)', DownloadFile),
                                      ('/mail', MailPage),
                                      (r'/maildetails/(.*)', MailDetailsPage),
                                      ('/settings', UserSettingsPage),
                                      (r'/download_zip/(.*)', DownloadZipFile),
                                      ],
                                     debug=settings.DEBUG)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
