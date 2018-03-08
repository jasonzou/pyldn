import os.path
import cherrypy

from lib import pyldnConst
#from lib import Receiver

import logging
import requests
from rdflib import Graph, URIRef, RDF, Namespace

# Logging
LOG_FORMAT = '%(asctime)-15s [%(levelname)s] (%(module)s.%(funcName)s) %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)

# Accepted content types
ACCEPTED_TYPES = ['application/ld+json',
                  'text/turtle',
                  'application/ld+json; profile="http://www.w3.org/ns/activitystreams', 'turtle', 'json-ld']

# Graph of the local inbox
ldp_url = URIRef("http://www.w3.org/ns/ldp#")
ldp = Namespace(ldp_url)

inbox_graph = Graph()
inbox_graph.add((URIRef(pyldnConst._inbox_url), RDF.type, ldp['Resource']))
inbox_graph.add((URIRef(pyldnConst._inbox_url), RDF.type, ldp['RDFSource']))
inbox_graph.add((URIRef(pyldnConst._inbox_url), RDF.type, ldp['Container']))
inbox_graph.add((URIRef(pyldnConst._inbox_url), RDF.type, ldp['BasicContainer']))
inbox_graph.bind('ldp', ldp)

# Dict for the notification graphs
# keys = graph names, values = rdflib.Graph()
graphs = {}

@cherrypy.expose
class Inbox(object): 

  _cp_dispatch = cherrypy.popargs('inboxId') 
  def GET(self,inboxId=None, *args, **kwargs):
    if inboxId:
        return self.get_notification(inboxId)

    request = cherrypy.serving.request
    resp = cherrypy.serving.response
    log.debug("Requested inbox data of {} in {}".format(request, request.headers['Accept']))
    if not request.headers['Accept'] or request.headers['Accept'] == '*/*' or 'text/html' in request.headers['Accept']:
        resp.body = inbox_graph.serialize(format='application/ld+json')
        resp.headers['Content-Type'] = 'application/ld+json'
    elif request.headers['Accept'] in ACCEPTED_TYPES:
        resp.body = inbox_graph.serialize(format=request.headers['Accept'])
        resp.headers['Content-Type'] = request.headers['Accept']
    else:
        return 'Requested format unavailable', 415

    resp.headers['X-Powered-By'] = 'https://github.com/jason/pyldn'
    resp.headers['Allow'] = "GET, HEAD, OPTIONS, POST"
    resp.headers['Link'] = '<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type", <http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'
    resp.headers['Accept-Post'] = 'application/ld+json, text/turtle'

    return resp.body

  def POST(self, *args, **kwargs):
    request = cherrypy.serving.request
    log.debug("Received request to create notification")
    log.debug("Headers: {}".format(request.headers))
    log.debug(request.path_info)
    log.debug(request.params)
    print(args)
    print(kwargs)
    
    dataLen = request.headers['Content-Length']
    print(dataLen)
    rawBody = request.body.read(int(dataLen))

    print(rawBody)
    # Check if there's acceptable content
    content_type = [s for s in ACCEPTED_TYPES if s in request.headers['Content-Type']]
    log.debug("Interpreting content type as {}".format(content_type))
    if not content_type:
        return 'Content type not accepted' #500
    if int(dataLen) <=0 :
        return 'Received empty payload' # 500

    resp = cherrypy.serving.response

    pyldnConst._ldn_counter += 1

    ldn_url = pyldnConst._inbox_url + '/' + str(pyldnConst._ldn_counter)
    print(ldn_url)
    graphs[ldn_url] = g = Graph()
    try:
        g.parse(data=rawBody, format=content_type[0])
    except: # Should not catch everything
        return 'Could not parse received {} payload'.format(content_type[0]) # 500

    log.debug('Created notification {}'.format(ldn_url))
    inbox_graph.add((URIRef(pyldnConst._inbox_url), ldp['contains'], URIRef(ldn_url)))
    resp.headers['Location'] = ldn_url

    print(inbox_graph.serialize(format='text/turtle'))
    resp.status = 201
    return ldn_url

  def get_notification(self,id):
    request = cherrypy.serving.request
    log.debug("Requested notification data of {}".format(request.path_info))
    log.debug("Headers: {}".format(request.headers))

    # Check if the named graph exists
    log.debug("Dict key is {}".format(pyldnConst._inbox_url + '/' + id))

    resp = cherrypy.serving.response
    if pyldnConst._inbox_url + '/' + id not in graphs:
        resp.status = 404
        return 'Requested notification does not exist'

    if 'Accept' not in request.headers or request.headers['Accept'] == '*/*' or 'text/html' in request.headers['Accept']:
        resp.body = graphs[pyldnConst._inbox_url + '/' + id].serialize(format='application/ld+json')
        resp.headers['Content-Type'] = 'application/ld+json'
    elif request.headers['Accept'] in ACCEPTED_TYPES:
        resp.body = graphs[pyldnConst._inbox_url +  '/' +  id].serialize(format=request.headers['Accept'])
        resp.headers['Content-Type'] = request.headers['Accept']
    else:
        resp.status = 415
        return 'Requested format unavailable' #, 415

    resp.headers['X-Powered-By'] = 'https://github.com/jason/pyldn'
    resp.headers['Allow'] = "GET"

    return resp.body

@cherrypy.expose
class Receiver(object):
  
  def handle_get_post(self, reqMethod):
    _inbox_url = 'http://localhost:8087/inbox/'
    resp = cherrypy.serving.response
    resp.headers['X-Powered-By'] = 'https://github.com/jasonzou/pyldn'
    linkStr = '<' + _inbox_url + '>; rel="http://www.w3.org/ns/ldp#inbox", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type"'
    log.info(linkStr)
    resp.headers['Link'] =  linkStr
    data = "hello --".join(str(reqMethod))
    resp.body = data.encode('utf8')
    resp.headers['Content-Length'] = str(len(resp.body))
    return resp.body

  def GET(self):
    return self.handle_get_post('GET')
  
  _cp_dispatch = cherrypy.popargs('inboxId') 
  def HEAD(self, inboxId=None, *args, **kwargs):
    print(inboxId)
    resp = cherrypy.serving.response
    resp.headers['X-Powered-By'] = 'https://github.com/jasonzou/pyldn'
    resp.headers['Allow'] = "GET, HEAD, OPTIONS, POST"
    resp.headers['Link'] = '<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type", <http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'
    resp.headers['Accept-Post'] = 'application/ld+json, text/turtle'

    return ''
    #return self.handle_get_post('HEAD')

  def POST(self, *args, **kwargs):
    print(args)
    print(kwargs)
    return 'fasdjjadfsfjklda'
    return self.handle_get_post('POST')

  _cp_dispatch = cherrypy.popargs('inboxId') 
  def OPTIONS(self,inboxId=None, *args, **kwargs):
    print(args)
    print(kwargs)
    print(inboxId)
    resp = cherrypy.serving.response
    resp.headers['X-Powered-By'] = 'https://github.com/jasonzou/pyldn'
    resp.headers['Allow'] = "GET, HEAD, OPTIONS, POST"
    resp.headers['Link'] = '<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type", <http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'
    resp.headers['Accept-Post'] = 'application/ld+json, text/turtle'

    return ''
class LDNReceiverServer(object):
    users = None
    rootServer = None
    config = None

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(current_dir, 'static')        
        log.info(current_dir)
        log.info(static_dir)
        self.config = {'/': {'log.error_file' :"logs/error.log",
                             'log.access_file' : "logs/access.log",
                             'log.screen' : True,
                             #'tools.encode.on' : True, 
                             #'tools.encode.encoding': "utf-8",
                             #'tools.decode.on': True,
                             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                             'tools.staticdir.root': static_dir },
                       '/static': {'tools.gzip.on': True,
                                   'tools.staticdir.on':True,
                                   'tools.staticdir.dir': '' },
                       '/static/css': {'tools.gzip.mime_types':['text/css'],
                                        'tools.staticdir.dir': 'css'},
                       '/static/js': {'tools.gzip.mime_types': ['application/javascript'],
                                       'tools.staticdir.dir': 'js'},
                       '/static/img': {'tools.staticdir.dir': 'images'},
                       '/favicon.ico': {'tools.staticfile.on':True,
                                        'tools.staticfile.filename':
                                        "favicon.ico", },
}


               
        
    def start(self):
        self.rootServer = Receiver() 
        self.rootServer.inbox = Inbox()
        cherrypy.config.update(pyldnConst.GLOBALCONFIG) 
        cherrypy.tree.mount(self.rootServer, "/", config=self.config)

        cherrypy.engine.start()

if __name__ == '__main__':
    test = LDNReceiverServer()
    test.start()
