# -*- coding: utf-8 -*-

import sys
import os
import re
import argparse
from unidecode import unidecode
import unicodedata
import urllib
from StringIO import StringIO
import gzip

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse

# import urllib3
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, FileTransferSpeed, FormatLabel, Percentage, ProgressBar, ReverseBar, RotatingMarker, SimpleProgress, Timer

def dlProgress(count, blockSize, totalSize):
    if pbar.maxval is None:
        pbar.maxval = totalSize
        pbar.start()
    try:
    	pbar.update(min(count*blockSize, totalSize))
    except Exception, e:
    	# print "\n\n--" + e.message + "--\n\n"
    	pass

def get_html_content(url):
	# usock = urllib2.urlopen(url)
	# data = usock.read()
	# usock.close()

	try:
		request = urllib2.Request(url)
		request.add_header('Accept-encoding', 'gzip')
		response = urllib2.urlopen(request)
		if response.info().get('Content-Encoding') == 'gzip':
		    buf = StringIO( response.read())
		    f = gzip.GzipFile(fileobj=buf)
		    data = f.read()
		else:
			data = response.read()

		return data
	except Exception, e:
		raise e

# Define arguments
parser=argparse.ArgumentParser()
parser.add_argument('-single', help = 'single file url')
parser.add_argument('-album', help = 'album url')
parser.add_argument('-o', help = 'output folder')
parser.add_argument('-xml', help = 'xml')
args=parser.parse_args()

if args.single:
	url = args.single
	pattern = re.compile(r'http://mp3\.zing\.vn/xml/song-xml/.*&')

if args.album:
	url = args.album
	pattern = re.compile(r'http://mp3\.zing\.vn/xml/album-xml/.*&')

try:
	if not args.xml:
		# GET XML

		data = get_html_content(url)
		matches =  pattern.findall(data)
		xml = matches[0][:-1]
	else:
		xml = args.xml

	data = get_html_content(xml)

	# Create output folder
	if args.o:
		output = args.o
	else:
		output = '.'

	if not os.path.exists(output):
		os.makedirs(output)

	data = re.sub(r'\n', '', data)

	# Get song list
	item_pattern = re.compile(r'<item type="mp3">.*?</item>')
	album_matches = item_pattern.findall(data)
	for item in album_matches:
		song_name = re.search(r'<title><!\[CDATA\[(.*)]]></title>', item)
		song_name = song_name.group(1)

		artist = re.search(r'<performer><!\[CDATA\[(.*)]]></performer>', item)
		artist = artist.group(1)

		source = re.search(r'<source><!\[CDATA\[(.*)]]></source>', item)
		source = source.group(1)

		filename = artist + "-" + song_name + ".mp3"
		filename = os.path.join(output, filename)

		widgets = [song_name + ": ", Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
		pbar = ProgressBar(widgets=widgets)

		urllib.urlretrieve(source, filename, reporthook=dlProgress)
		pbar.finish()

except Exception, e:
	print "\n\n--" + e.message + "--\n\n"
	raise e
