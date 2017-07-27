import os
import sys
sys.platform = 'linux3'

import logging
from google.appengine.ext import ndb
import re

class authorization(ndb.Model):
   organization = ndb.StringProperty(required=True)
   email = ndb.StringProperty(required=True)
   role = ndb.StringProperty(required=True)
   mgEmail = ndb.StringProperty(required=True)
   firstName = ndb.StringProperty()
   lastName = ndb.StringProperty()
   authCreated = ndb.DateTimeProperty(auto_now_add=True)
   authUpdated = ndb.DateTimeProperty(auto_now=True)

def initializeAmberleaAuth(role):
   ndb.put_multi([
      authorization(
         key = ndb.Key('authorization','amberleachurch@gmail.com-{}'.format(role)),
         organization = 'Amberlea Presbyterian Church',
         email = 'amberleachurch@gmail.com',
         mgEmail = 'info@amberleachurch.ca',
         role = 'Bulk Mail',
         firstName = 'Amberlea',
         lastName = 'Church'),
      authorization(
         key = ndb.Key('authorization','gregbwatson@gmail.com-{}'.format(role)),
         organization = 'Amberlea Presbyterian Church',
         email = 'gregbwatson@gmail.com',
         mgEmail = 'info@amberleachurch.ca',
         role = 'Bulk Mail',
         firstName = 'Greg',
         lastName = 'Watson'),
      authorization(
         key = ndb.Key('authorization','ndvarga@gmail.com-{}'.format(role)),
         organization = 'Amberlea Presbyterian Church',
         email = 'ndvarga@gmail.com',
         mgEmail = 'familyministries@amberleachurch.ca',
         role = 'Bulk Mail',
         firstName = 'Nancy',
         lastName = 'Varga'),
      authorization(
         key = ndb.Key('authorization','rosecsgro@gmail.com-{}'.format(role)),
         organization = 'Amberlea Presbyterian Church',
         email = 'rosecsgro@gmail.com',
         mgEmail = 'info@amberleachurch.ca',
         role = 'Bulk Mail',
         firstName = 'Rose',
         lastName = 'Morrison'),
      authorization(
         key = ndb.Key('authorization','monascrivens@gmail.com-{}'.format(role)),
         organization = 'Amberlea Presbyterian Church',
         email = 'monascrivens@gmail.com',
         mgEmail = 'revmona@amberleachurch.ca',
         role = 'Bulk Mail',
         firstName = 'Mona',
         lastName = 'Scrivens'),
      authorization(
         key = ndb.Key('authorization','tmjow@bell.net-{}'.format(role)),
         organization = 'Amberlea Presbyterian Church',
         email = 'tmjow@bell.net',
         mgEmail = 'ted@amberleachurch.ca',
         role = 'Bulk Mail',
         firstName = 'Ted',
         lastName = 'Jowett')])
   return

def isOkSender(sender, role):
   """
   isOkSender() Returns:
      sender is member of group = True, anything else, False
   """
   
   retcode = ''

   try:
      lookup1 = re.search(r'([\w\.-]+)(@[\w\.-]+)', sender)
      lookup_email = re.sub('\.','',lookup1.group(1)) + lookup1.group(2)
      logging.info('isOkSender lookup_email= "{}"'.format(lookup_email))
   except:
      logging.info('isOkSender failed to extract email from {}'.format(sender))
      return retcode

   amberlea_Owner_key = ndb.Key(
      'authorization','amberleachurch@gmail.com-{}'.format(role))
   amberlea_Owner = amberlea_Owner_key.get()
   if amberlea_Owner == None:
      logging.info('isOkSender initializing "authorization" datastore')
      initializeAmberleaAuth(role)

   logging.info('isOkSender looking-up key {}-{}'.format(lookup_email, role))
   amberlea_key = ndb.Key(
      'authorization', '{0}-{1}'.format(lookup_email, role))
   amberlea_auth = amberlea_key.get()
   if amberlea_auth is not None:
      logging.info('isOkSender found key {}-{} returning "{}"'.format(
         lookup_email, 
         role, 
         amberlea_auth.mgEmail))
      retcode = amberlea_auth.mgEmail

   return retcode
   
if __name__ == '__main__':
   print isOkSender('gregbwatson@gmail.com','{}'.format(role)) # good case
   print isOkSender('elsiemwatson@gmail.com','{}'.format(role)) # bad case
