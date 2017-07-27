import os
import sys
sys.platform = 'linux3'

import logging
import re
import requests, requests_toolbelt.adapters.appengine
import webapp2
import json
import datetime
from google.appengine.api import mail

import checkSender
import notify
import BuildMassMailObj
import enqueueMailMsg

class IncomingMailHandler(webapp2.RequestHandler):
   def post(self):
      msg = mail.InboundEmailMessage(self.request.body)
      logging.info('msg received, "{0}" from "{1}"'.format(msg.subject, msg.sender))
      if isinstance(msg.to, list):
         ListName1 = re.search('(.*)@', msg.to[0])
      else:
         ListName1 = re.search('(.*)@', msg.to)
      logging.info('To email: {0}'.format(ListName1))
      ListName1 = re.search('(.*)@', msg.to)
      ListName = ListName1.group(1)
      mgEmail = checkSender.isOkSender(msg.sender, 'BulkMail')
      if len(mgEmail) > 0:
         logging.info('maillinglist Name: {0}'.format(ListName))
         requests_toolbelt.adapters.appengine.monkeypatch()
         stUrl = 'https://script.google.com/macros/s/AKfycbzg_WydKXAczuzgOr9XpbidYA33lGlyvNwudNCTs0GH65ksIXY/exec?list=' + ListName + '&'
         if os.environ['SERVER_SOFTWARE'].startswith('Development'):
            listTo = [["Watson, Greg", "gregbwatson@gmail.com"]]
         else:
            resp = requests.get(stUrl)
            logging.info('mailing list lookup status: {0}'.format(resp.status_code))
            listTo = resp.content
            logging.info('receivemail listTo {0}'.format(listTo))
            if not isinstance(listTo, list):
               if re.search('no_email_found',listTo[0])==None:
                  listTo = eval(listTo)
               else:
                  logging.info('no_email_found for list "{}"'.format(ListName))
                  listTo = []
         if len(listTo) > 0:
            msgKey = BuildMassMailObj.Build_massMailMsg(msg, listTo, mgEmail)
            logging.info('enqueuing bulk mail')
            enqueueMailMsg.addToQueue(msgKey)
            stLog = '<tr><td align="center" colspan=3><font color="blue"><b>Email Enqueued to Send</b></td></tr>'
            for arrTo in listTo:
               if len(arrTo) > 1:
                  stLog += '\n<tr><td align="right"><font color="blue">{}</td><td>{}</td><td><b>PENDING</b></td></tr>'.format(arrTo[0], arrTo[1])
            notify.notifyMasters(
               msg.sender, 
               msg.subject, 
               stLog,
               'Massmailing requested {0} enqueued for lists "{1}"'.format(datetime.datetime.today().strftime('%Y-%m-%d '), ListName),
               mgEmail,
               ListName)
         else:
            notify.notifyMasters(
               msg.sender, 
               msg.subject, 
               '<tr><td align="center"><font color="red"><b>WARNING!</b> No email addresses found for list, "' + msg.to + '"</td></tr>',
               'Massmailing requested {0} FAILED for lists "{1}"'.format(datetime.datetime.today().strftime('%Y-%m-%d '), ListName),
               mgEmail,
               ListName)
      else:
         notify.notifyMasters(
            'amberleachurch@gmail.com', 
            msg.subject, 
            '<tr><td align="center"><font color="red"><b>WARNING!</b> Unauthorized email received from, "{0}". <font color="red">No emails sent.</font></td></tr>'.format(msg.sender),
            'Massmailing requested {0} by UNAUTHORIZED requestor "{1}"'
               .format(datetime.datetime.today().strftime('%Y-%m-%d '), msg.sender),
            'no authorized "from" address found',
            ListName)
      return

application = webapp2.WSGIApplication([('/_ah/mail/.+', IncomingMailHandler)], debug=True)

if __name__ == '__main__':
    run_wsgi_app(application)