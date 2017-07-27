mailgun=True

import os
import sys
sys.platform = 'linux3'

import requests, requests_toolbelt.adapters.appengine
import webapp2
import logging
import re
import base64 
import datetime

from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.ext import ndb

import notify
import BuildMassMailObj
import enqueueMailMsg
import gbw_utils

class dummyMail():
   status_code = 250

class sntMail(ndb.Model):
   emailAddress = ndb.StringProperty()
   emailSubject = ndb.StringProperty()
   date_sent = ndb.DateTimeProperty(auto_now_add=True)

# [START config]
MAILGUN_DOMAIN_NAME = 'mail.amberleachurch.ca'
MAILGUN_API_KEY = 'key-dc56bd02d2525e84ccf9093a6b3e6774'
# [END config]

def isDuplicate(stTo, stSubject):
   """
   Check if the combination of to-email and subject has been sent before
   result: True if sent, False if not sent
   """
   stKey = '{0}-{1}'.format(stTo, stSubject)
   msgsnt_key = ndb.Key('sntMail', stKey)
   msgsnt = msgsnt_key.get()
   if msgsnt is not None:
      retcode = 'TRUE'
   else:
      retcode = 'FALSE'
   logging.info('isDuplicate ndb.Key(\'sntMail\', "{0}")={1}'.format(stKey, retcode))
   return msgsnt is not None

def logSnt(stTo, stSubject):
   """
   Record every email sent using the to-email and subject to create the key
   result: datastore entity record created
   """
   stKey = '{0}-{1}'.format(stTo, stSubject)
   logging.info('logSnt( "{0}" )'.format(stKey))
   msgsnt_key = ndb.Key('sntMail', stKey)
   msgsnt = sntMail(
      key = msgsnt_key,
      emailAddress = stTo,
      emailSubject = stSubject)
   msgsnt.put()
   return

def getSntCnt():
   """
   Count the number of email sent within the hour. Reset every 3600 seconds
   result: integer count of email sent
   """
   data = memcache.get('MassMailSnt_Amberlea')
   if data is None:
      return 0
   return data

def addSntCnt():
   """
   Count the number of email sent within the hour. Reset every 3600 seconds
   result: integer count of email sent
   """
   data = memcache.get('MassMailSnt_Amberlea')
   if data is not None:
      memcache.incr('MassMailSnt_Amberlea')
      data = memcache.get('MassMailSnt_Amberlea')
   else:
      memcache.add(key='MassMailSnt_Amberlea', value=1, time=3600)
      data = memcache.get('MassMailSnt_Amberlea')
   logging.info('memcache value= {}'.format(data))
   return data

def isOkEmail(stEmail):
   return re.search('[^@]+@[^@]+\.[^@]+', stEmail) is not None

class MailToSend(webapp2.RequestHandler):
   def post(self):
      listOut = []
      stLog = ''
      urlMG = 'https://api.mailgun.net/v3/{0}/messages'.format(MAILGUN_DOMAIN_NAME)
      logging.info('~~Task START~~')
      key_str = self.request.get('mailtosendkey')
      logging.info('key_str: {0}'.format(key_str))
      key = ndb.Key(urlsafe=key_str)
      try:
         msg = key.get() # if the key does not exist, quit
      except:
         return
      logging.info('mgEmail: {0}'.format(msg.mgEmail))
      logging.info('originator: {0}'.format(msg.sender))
      logging.info('subject: {0}'.format(msg.subject))
      originator = msg.sender
      subject = msg.subject
      html = msg.body_html
      listTo = msg.listTo
      mgEmail = msg.mgEmail
      logging.info ('firemailgun listTo: {0}'.format(listTo))
      if not isinstance(listTo, list):
         if re.search('no_email_found', listTo) == None:
            listTo = eval(listTo)
         else:
            logging.info('no_email_found for list "{}"'.format(subject))
            listTo = [['','']]
      logging.info ('firemailgun listTo[0][1]: {0}'.format(listTo[0][1]))
      attached = []
      blContinue = True
      requests_toolbelt.adapters.appengine.monkeypatch()
      if os.environ['SERVER_SOFTWARE'].startswith('Development'):
         logging.info('firing mailgun')
      else:
         if hasattr(msg, 'attached'):
            for aF in msg.attached:
               logging.info('firemailgun aF: "{0}", "{1}"'.format(aF.attachType, aF.filename))
               payload = aF.payload
               attached.append((aF.attachType, (aF.filename, payload)))
         listOut = []
         stLog = ''
         for stTo in listTo:
            if isOkEmail(stTo[1])==False:
               logging.info('invalid email address "{0} <{1}>"'.format(stTo[0],stTo[1]))
               stLog += '<tr><td align="right"><font color="red">' + stTo[0] + '</td><td>' + stTo[1] + '</td><td align="center"><b>INVALID EMAIL</b></td></tr>\n'
            else:
               if isDuplicate(stTo[1], subject):
                  stLog += '<tr><td align="right"><font color="red">' + stTo[0] + '</td><td>' + stTo[1] + '</td><td align="center"><b>ALREADY SENT</b></td></tr>\n'
               else:
                  if blContinue==False or getSntCnt() > 90:
                     listOut.append(stTo)
                     stLog += '<tr><td align="right"><font color="red">' + stTo[0] + '</td><td>' + stTo[1] + '</td><td align="center"><b>PENDING</b></td></tr>\n'
                  else:
                     logging.info('mail to: {0}, from "{1}" about "{2}"'.format(stTo[1], mgEmail, subject))
                     data = {
                        'from': mgEmail,
                        'to': stTo[1],
                        'subject': subject,
                        'text': re.sub(r'~youremail~',stTo[1],html),
                        'html': re.sub(r'~youremail~',stTo[1],html)}
                     if len(attached) > 0:
                        logging.info('sending email with attachements')
                        if mailgun:
                           outRequest = requests.post(urlMG, auth=('api',MAILGUN_API_KEY), files=attached, data = data)
                        else:
                           outRequest = dummyMail
                     else:
                        logging.info('sending email without attachements')
                        if mailgun:
                           outRequest = requests.post(urlMG, auth=('api',MAILGUN_API_KEY), data = data)
                        else:
                           outRequest = dummyMail
                     logging.info('outRequest.status_code: {0}'.format(outRequest.status_code))
                     if outRequest.status_code < 400:
                        addSntCnt()
                        stLog += '<tr><td align="right"><font color="green">' + stTo[0] + '</td><td>' + stTo[1] + '</td><td align="center"><b>SENT</b></td></tr>\n'
                        logSnt(stTo[1], subject)
                     else:
                        blContinue = False
                        listOut.append(stTo)
                        stLog += '<tr><td align="right"><font color="red">' + stTo[0] + '</td><td>' + stTo[1] + '</td><td align="center"><b>PENDING</b></td></tr>\n'
         #end of mailing list loop
      logging.info('len(listOut): {0}'.format(len(listOut)))
      if len(listOut) > 0:
         msg = key.get()
         msg.listTo = listOut
         msg.put()
         enqueueMailMsg.addToQueue(key_str)
      else:
         logging.info('deleting datastore for key_str: {0}'.format(key_str))
         key.delete()
      notify.notifyMasters(
         originator, 
         subject, 
         stLog,
         'Massmailing RESULTS {0} for mailing requested by "{1}"'.format(datetime.datetime.today().strftime('%Y-%m-%d '), originator),
         mgEmail)
      logging.info('~~Task END~~')
      return 

application = webapp2.WSGIApplication([('/_ah/queue/mailtosend', MailToSend)], debug=True)

if __name__ == '__main__':
    run_wsgi_app(application)