import os
import sys
sys.platform = 'linux3'

from google.appengine.api import taskqueue

def addToQueue(mailtosendKey):
   try:
      taskqueue.add(queue_name="mailtosend",params={'mailtosendkey' : mailtosendKey}, countdown=3600)
      return True
   except taskqueue.DuplicateTaskNameError, e:
      return False

if __name__ == '__main__':
   pass