# pyldn: A python Linked Data Notifications (LDN) receiver

import logging
import requests
from rdflib import Graph, URIRef, RDF, Namespace

import cherrypy

# pyldn modules
from pyldnconfig import Pyldnconfig

@cherrypy.expose
class Receiver(object):
  def GET(self):
    resp = cherrypy.response
    resp.headers['X-Powered-By'] = 'https://github.com/jasonzou/pyldn'
    resp.headers['Link'] =  '<' + pyldnconf._inbox_url + '>; rel="http://www.w3.org/ns/ldp#inbox", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type"'

    return resp
