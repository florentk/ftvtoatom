#!/usr/bin/python3
# coding: utf8

from datetime import datetime
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.request import urlopen 
from urllib.error import HTTPError

APP_NAME = u'ftvtoatom'
APP_LINK = u'https://bitbucket.org/florent_k/ftvtoatom'
APP_VERSION = u'0.2'

PORT_NUMBER = 58080
DOMAIN = u'https://www.france.tv'

DURATION_MIN=25

def generate_entry(e,date):
  e=[u'\n<entry>',
    u'\t<title>' + e['title'] + u'</title>',
    u'\t<link href="' + DOMAIN + e['link'] + u'"/>',
    u'\t<id>' + e['uid'] + u'</id>',
    u'\t<updated>' + date.isoformat("T") + u"Z" + u'</updated>',
    u'\t<summary>' + e['content'] + u'</summary>' ,
    u'</entry>']
  return '\n'.join(e)


def generate_atom(title,link,emissions):
  date =  datetime.utcnow()
  atom_pref=[u'<?xml version="1.0" encoding="utf-8"?>',u'<feed xmlns="http://www.w3.org/2005/Atom">']
  atom_header = [
    u'<title>' + title + u'</title>',
    u'<link href="' + link + u'"/>',
    u'<updated>' + date.isoformat("T")  + u"Z" + u'</updated>',
    u'<generator uri="' + APP_LINK + u'" version="' + APP_VERSION + u'">',
    u'\t' + APP_NAME,
    u'</generator>']
  atom_entry = [generate_entry(e,date) for e in emissions]
  atom_suffix = [u'</feed>']

  return '\n'.join(atom_pref + atom_header + atom_entry + atom_suffix)



def extract_element(v):
	content = v.text
	metadatas = v.find_all('span',class_='c-metadata')
	
	if (len(metadatas) == 2):
	  date = metadatas[0].text
	  duration = int(metadatas[1].text.split()[0])
	elif (len(metadatas) == 1):
	  date = ""
	  duration = int(metadatas[0].text.split()[0])
	else:
	  date = ""
	  duration = 0
	  
	a = v.find(class_='c-card-video__textarea').h3.a
	link = a['href']
	title = a.find('div',class_='c-card-video__title').text
	desc_div=a.find('div',class_='c-card-video__description')
	if(desc_div):
	  desc = desc_div.text
	else:
	  desc = ""
	uid = a['href']
	return {"link":link,"title":"%s - %s" % (title,desc),"content":content,"uid":uid,"duration":duration,"date":date}
	
def get_emissions(s):
	return [ extract_element(v) for v in s.find_all("div", class_='c-card-video') ]


title = u"France Tv Documentaires"
url_pattern = u"%s/%s/contents"



class MyHandler(BaseHTTPRequestHandler):
	def do_GET(s):
		url = url_pattern % (DOMAIN,s.path)
		try:
			emissions = get_emissions(BeautifulSoup(urlopen(url),"lxml"))
			s.send_response(200)
			s.send_header("Content-type", "application/atom+xml")
			s.end_headers()
			s.wfile.write(bytes(generate_atom(title,url,filter(lambda e : e['duration'] >= DURATION_MIN, emissions)),"utf8"))
		except HTTPError:
			s.send_error(404,"Page not found")

def main():
    try:
        server = HTTPServer(('', PORT_NUMBER), MyHandler)
        print ('Started ftvtoatom...')
        server.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down server')
        server.socket.close()


def test():
	emissions = get_emissions(BeautifulSoup(urlopen(url),"lxml"))
	print (generate_atom(title,url,emissions))

if __name__ == "__main__":
  main()




	

