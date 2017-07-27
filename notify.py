import os
import sys
sys.platform = 'linux3'

import logging
import datetime
from google.appengine.api import mail

def notifyMasters(stTo, subject, stLog, notify_Sbj='', stMgEmail = 'not defined', stList='already expanded'):

   outSbj = ''
   if len('Status mass mail requested {0}'.format(datetime.datetime.today().strftime('%Y-%m-%d '))) > 0:
      outSbj = notify_Sbj
   else:
      outSbj = 'Status mass mail requested {0}'.format(datetime.datetime.today().strftime('%Y-%m-%d '))

   html_body = """
<p>Hi,</p>
<p>We have processed the following mass mail job.</p>
<table>
<tr><td><b>Parameter</td><td><b>Values</td></tr>
<tr><td align="right"><font color="red">Date:</td><td>{0}</td></tr>
<tr><td align="right"><font color="red">Originator:</td><td>{1}</td></tr>
<tr><td align="right"><font color="red">Subject:</td><td>{2}</td></tr>
<tr><td align="right"><font color="red">From:</td><td>{3}</td></tr>
<tr><td align="right"><font color="red">List(s):</td><td>{4}</td></tr>
</table>
<br>
<table border="0">
{5}
</table>
<br>
<p>Blessings</p>
""".format(datetime.datetime.today().strftime('%Y-%m-%d '), stTo, subject, stMgEmail, stList, stLog)

   mail.send_mail(
      sender='amberleachurch@gmail.com',
      to=stTo,
      bcc='gregbwatson@gmail.com',
      subject=outSbj,
      body=html_body,
      html=html_body)
   return

if __name__ == '__main__':
   pass
