#!/usr/bin/python3
# coding: utf8

from datetime import datetime
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.request import urlopen 

APP_NAME = u'ftvtoatom'
APP_LINK = u'https://bitbucket.org/florent_k/ftvtoatom'
APP_VERSION = u'0.1'
PORT_NUMBER = 58080

def generate_entry(e,date):
  e=[u'\n<entry>',
    u'\t<title>' + e['title'] + u'</title>',
    u'\t<link href="' + e['link'] + u'"/>',
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



def extract_element(li):
	attrs = dict(li.find('a').attrs)
	link = attrs['href']
	title = attrs['title']
	uid = attrs['data-video']
	content = r"\n".join([ p.string.strip() for p in li.find('div', {"class": "card-content"}).findAll('p')])
	return {"link":link,"title":title,"content":content,"uid":uid}
	
def get_emissions(s):
	return [ extract_element(li) for li in s.findAll("li") ]


title = u"France Tv Documentaires"
url = u"https://www.france.tv/documentaires/contents"



class MyHandler(BaseHTTPRequestHandler):
	def do_GET(s):
		if(s.path == "" or s.path == "/"):
			emissions = get_emissions(BeautifulSoup(urlopen(url),"lxml"))
			s.send_response(200)
			s.send_header("Content-type", "application/atom+xml")
			s.end_headers()
			s.wfile.write(bytes(generate_atom(title,url,emissions),"utf8"))
		else:
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




	

