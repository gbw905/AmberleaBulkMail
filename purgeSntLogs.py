import os
import sys
sys.platform = 'linux3'

import logging
import datetime
import webapp2

from google.appengine.ext import ndb

class sntMail(ndb.Model):
   emailAddress = ndb.StringProperty()
   emailSubject = ndb.StringProperty()
   date_sent = ndb.DateTimeProperty(auto_now_add=True)

def purge_mailSntLogs():
   logging.info('"purge_mailSntLogs" called')   
   earliest = datetime.datetime.now() - datetime.timedelta(days=3)
   logging.info('"earliest" cutoff date calculated as {}'.format(earliest))   
   sntMail_keys = sntMail.query(sntMail.date_sent <= earliest).fetch(keys_only=True)
   try:
      ndb.delete_multi(sntMail_keys)
      logging.info('ndb.delete_multi(sntMail_keys) SUCCESS')
   except:
      logging.info('ndb.delete_multi(sntMail_keys) FAILED')
   return 'done'

class CleanSntMailLogs(webapp2.RequestHandler):
   def get(self):
      logging.info('"CleanSntMailLogs" about to call "purge_mailSntLogs"')   
      self.response.write(purge_mailSntLogs())

application = webapp2.WSGIApplication([('/tasks/clean_sntMail', CleanSntMailLogs)], debug=True)

if __name__ == '__main__':
    run_wsgi_app(application)