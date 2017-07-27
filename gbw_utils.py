import os
import sys
sys.platform = 'linux3'

import re
import logging

EXTENSION_MIME_MAP = {
    'aif': 'audio/x-aiff',
    'aifc': 'audio/x-aiff',
    'aiff': 'audio/x-aiff',
    'asc': 'text/plain',
    'au': 'audio/basic',
    'avi': 'video/x-msvideo',
    'bmp': 'image/x-ms-bmp',
    'css': 'text/css',
    'csv': 'text/csv',
    'doc': 'application/msword',
    'docx': 'application/msword',
    'diff': 'text/plain',
    'flac': 'audio/flac',
    'gif': 'image/gif',
    'gzip': 'application/x-gzip',
    'htm': 'text/html',
    'html': 'text/html',
    'ics': 'text/calendar',
    'jpe': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'kml': 'application/vnd.google-earth.kml+xml',
    'kmz': 'application/vnd.google-earth.kmz',
    'm4a': 'audio/mp4',
    'mid': 'audio/mid',
    'mov': 'video/quicktime',
    'mp3': 'audio/mpeg',
    'mp4': 'video/mp4',
    'mpe': 'video/mpeg',
    'mpeg': 'video/mpeg',
    'mpg': 'video/mpeg',
    'odp': 'application/vnd.oasis.opendocument.presentation',
    'ods': 'application/vnd.oasis.opendocument.spreadsheet',
    'odt': 'application/vnd.oasis.opendocument.text',
    'oga': 'audio/ogg',
    'ogg': 'audio/ogg',
    'ogv': 'video/ogg',
    'pdf': 'application/pdf',
    'png': 'image/png',
    'pot': 'text/plain',
    'pps': 'application/vnd.ms-powerpoint',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.ms-powerpoint',
    'qt': 'video/quicktime',
    'rmi': 'audio/mid',
    'rss': 'text/rss+xml',
    'snd': 'audio/basic',
    'sxc': 'application/vnd.sun.xml.calc',
    'sxw': 'application/vnd.sun.xml.writer',
    'text': 'text/plain',
    'tif': 'image/tiff',
    'tiff': 'image/tiff',
    'txt': 'text/plain',
    'vcf': 'text/directory',
    'wav': 'audio/x-wav',
    'wbmp': 'image/vnd.wap.wbmp',
    'webm': 'video/webm',
    'webp': 'image/webp',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.ms-excel',
    'zip': 'application/zip'
    }

EXTENSION_BLACKLIST = [
    'ade',
    'adp',
    'bat',
    'chm',
    'cmd',
    'com',
    'cpl',
    'exe',
    'hta',
    'ins',
    'isp',
    'jse',
    'lib',
    'mde',
    'msc',
    'msp',
    'mst',
    'pif',
    'scr',
    'sct',
    'shb',
    'sys',
    'vb',
    'vbe',
    'vbs',
    'vxd',
    'wsc',
    'wsf',
    'wsh',
    ]

def _GetMimeType(file_name):
   """Determines the MINE type from the file name.

   This function parses the file name and determines the MIME type based on
   an extension map.

   This method is not part of the public API and should not be used by
   applications.

   Args:
      file_name: File for which you are attempting to determine the extension.

   Returns:
      The MIME type that is associated with the file extension.

   Raises:
       InvalidAttachmentTypeError: If the file type is invalid.
   """
   extension_index = file_name.rfind('.')
   if extension_index == -1:
      extension = ''
   else:
      extension = file_name[extension_index + 1:].lower()
   if extension in EXTENSION_BLACKLIST:
      return None
      logging.info('Extension %s is not supported.' % extension)
   mime_type = EXTENSION_MIME_MAP.get(extension, None)
   if mime_type is None:
      mime_type = 'application/octet-stream'
   return mime_type

def isImage(file_name):
   return _GetMimeType(file_name).startswith("image")

def toASCII(strIn):
   # remove non-ascii characters from string
   strOut = re.sub(r'[^\x00-\x7F]+','', strIn)
   return strOut

def toSafeFileName(strIn):
   # convert to ascii and remove spaces from string
   strOut = toASCII(strIn)
   strOut = re.sub(r' ', '_', strOut)
   return strOut

def getCidList(stMg):
   arrInln = re.findall(r'<img src=\"cid:(\w*)\"\s',stMg)
   if arrInln is None:
      arrInln = []
   return arrInln

def updtCid(stCid, stFile, stMg):
   inCid=re.sub('<img src=\"cid:','',stCid)
   logging.info('stCid= "{0}", rCid="{0}"'.format(stCid, inCid))
   rCid = re.compile(inCid)
   return re.sub(rCid, stFile, stMg)

