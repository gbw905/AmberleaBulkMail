import os
import sys
sys.platform = 'linux3'

import logging
import os
import re
import json
import gbw_utils
from google.appengine.ext import ndb
from google.appengine.api import app_identity
from google.appengine.api import mail
import email

class attachedFile(ndb.Model):
   attachType = ndb.StringProperty()
   filename = ndb.StringProperty()
   payload = ndb.BlobProperty(indexed=False)

class massMailMsg(ndb.Model):
   sender = ndb.StringProperty(required=True)
   listTo = ndb.PickleProperty(required=True)
   subject = ndb.StringProperty(required=True)
   body_html = ndb.TextProperty(required=True)
   attached = ndb.StructuredProperty(attachedFile, repeated=True, indexed=False)
   mgEmail = ndb.StringProperty(required=True)
   created = ndb.DateTimeProperty(auto_now_add=True)

def getPayload(filecontents):
   payload = None
   if filecontents.encoding and filecontents.encoding.lower() != '7bit':
      try:
         payload = filecontents.payload.decode(filecontents.encoding)
      except LookupError:
         raise UnknownEncodingError('Unknown decoding %s.' % filecontents.encoding)
      except (Exception, Error), e:
         raise PayloadEncodingError('Could not decode payload: %s' % e)
   else:
      payload = filecontents.payload
   return payload

def Build_massMailMsg(msg, listTo, mgEmail):
   msgOut = massMailMsg(
      sender = msg.sender,
      subject = msg.subject,)

   #logging.info('Build_massMailMsg listTo: {0}'.format(listTo[0][1]))
   msgOut.listTo = listTo
   msgOut.mgEmail = mgEmail

   for content_type, body in msg.bodies('text/html'):
      body_html = body.decode()
   body_html = gbw_utils.toASCII(body_html)
   body_html += '<br><p align="center"><font color="green">To remove your email address from Amberlea Church mailing lists, click <b><a href="https://docs.google.com/forms/d/e/1FAIpQLSemVmpOK7dYVPGpHzoWhbEmiEpl8rX6t3Gf_2tncftvPsMarA/formResponse?entry.85201517=unsubscribe&entry.2066775521=~youremail~&submit=Submit" target="_blank">unsubscribe</a></b></font></p>';
   #logging.info('Build_massMailMsg body_html: {0}'.format(str(body_html)))

   arrAttchdIn = []
   arrCid = []
   arrAttchdOut = []
   if hasattr(msg, 'attachments'):
      logging.info('~~ start attachment processing ~~')
      if len(msg.attachments) == 2 and isinstance(msg.attachments[0], basestring):
         arrAttchdIn = [[msg.attachments[0], msg.attachments[1]]]
      else:
         arrAttchdIn = msg.attachments
      arrCid = gbw_utils.getCidList(body_html)
      logging.info('Build_massMailMsg inlineCnt= "{0}"'.format(len(arrCid)))
   if len(arrAttchdIn) > 0:
      logging.info('Build_massMailMsg {0} attachments found'.format(len(arrAttchdIn)))
      for a in range(len(arrAttchdIn)):
         aName, aPayload = arrAttchdIn[a]
         aNameASC = gbw_utils.toSafeFileName(aName)
         aType = gbw_utils._GetMimeType(aName)
         stAttachedType = ''
         if aType != None and len(aNameASC) > 0 and aNameASC != 'image.png':
            if a < len(arrCid):
               logging.info('Build_massMailMsg file "{2}" with arrCid[{0}]= "{1}" as "inline"'.format(a, arrCid[a], aNameASC))
               body_html = gbw_utils.updtCid(arrCid[a], aNameASC, body_html)
               stAttachedType='inline'
            else:
               logging.info('Build_massMailMsg append "{0}" as "attached"'.format(aName))
               stAttachedType='attachment'
         logging.info('Build_massMailMsg aF("{0}", "{1}", payload)'.format(stAttachedType, aNameASC))
         payload = getPayload(aPayload)
         aF = attachedFile(
            attachType = stAttachedType,
            filename = aNameASC,
            payload = payload)
         arrAttchdOut.append(aF)
      logging.info('~~ end attachment processing ~~')
   msgOut.body_html = body_html
   logging.info('Build_massMailMsg {0} files to load to msg.files'.format(len(arrAttchdIn)))
   msgOut.attached = arrAttchdOut
   msgOut.put()
   msgKey = msgOut.key
   logging.info('msgOut.put(): {0}'.format(msgKey.urlsafe()))
   return msgKey.urlsafe()

if __name__ == '__main__':
   pass