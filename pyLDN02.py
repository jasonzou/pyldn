#!/usr/bin/env python
#-*-coding:utf-8-*-
# vim: set filetype=python expandtab tabstop=2 shiftwidth=2 autoindent smartindent:

import cherrypy

from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import urlparse
from cherrypy.lib import httputil
from lib import pyldnTempl

from cherrypy.lib.cptools import accept
import pprint

from rdflib import *
import sys

import simplejson                                                              
import rdflib

from lib import pyldnConst

import time

import logging
log = logging.getLogger(__name__)

def handle_error():
    cherrypy.response.status = 500
    templ = pyldnTempl.loader.load('cct2http500.html')
    stream = templ.generate(status=500,message="Internal Server Error, please contact the site administrator jason.zou@gmail.com. ")
    response = stream.render('xhtml')
    cherrypy.response.body = [response]

class Thesaurus(object):
    _cp_config = {'request.error_response': handle_error}
       # 'tools.encode.on':True,
       # 'tools.encode.encoding':'utf-8'}
    def __init__(self, name):
        self.prefix = name;
        self.descList = []
        self.startime = time.time()
     
    exposed = True
    def GET(self):
        log.info('enter Root - Get')
        
        log.info("vis is 1" )
        #json = []
        #mainNodes = self.getQClass()
        mainNodes = [] 
        request = cherrypy.serving.request
        req_h = request.headers
        print(req_h)

        data = "hello".encode('utf8')
        dataLen = str(len(data))
        print(data)
        print(dataLen)
        respheaders = cherrypy.serving.response.headers
        respheaders['X-Powered-By'] = 'http://nkos.info'
        respheaders["Content-Type"] = 'text/html'
        respheaders["Server"]= "Null CherryPy"
        respheaders["Content-Length"] = dataLen
        
        cherrypy.serving.response.body = data
        return cherrypy.response

        #return print(request)
        
        #log("vis is 2" + mainNodes)
        #mainNodes = []
        #self.description()
        templStr = self.prefix+"Index.html"
        templ = pyldnTempl.loader.load(templStr)
        elapsedTime = time.time() - self.startime

        self.descList = []
        stream = templ.generate()
        return stream.render('xhtml')
    

class notImplemented(object):
    _cp_config = {'request.error_response': handle_error,
        'tools.encode.on':True,
        'tools.encode.encoding':'utf-8'}
    def __init__(self, name="cct2"):
        self.prefix = name
        self.descList = []
     
    exposed = True
    def GET(self):
        log.info('enter notImplemented - Get')
        
        #self.description()
        templStr = self.prefix+"IndexNotImplemented.html"
        templ = pyldnTempl.loader.load(templStr)
        stream = templ.generate(descs=self.descList,json=json)
        return stream.render('xhtml')
       

    
def receiver(): 
    """Start with the builtin server.""" 
    # Set up site-wide config. Do this first so that, 
    # if something goes wrong, we get a log. 
    log.info(cherrypy.request.remote.ip)
    log.info("+++++++++ ip ++++++++++++")

    root = Thesaurus('pyldn')

#    cherrypy.config.update({'error_page.404': error_page_404})
#    cherrypy.config.update({'error_page.405': error_page_405})
#    cherrypy.config.update({'error_page.500': error_page_500})

    cherrypy.config.update(pyldnConst.GLOBALCONFIG) 
    cherrypy.tree.mount(root, "/", config=pyldnConst.APPCONFIG)
   
    #log(str(cherrypy.config["tools.encode.on"]))
    #log(cherrypy.config["tools.encode.encoding"])
    

    #cherrypy.server.quickstart() 
    cherrypy.engine.start() 

if __name__ == "__main__": 
    receiver() 

