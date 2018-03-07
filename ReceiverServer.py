import os.path
import cherrypy

from lib import pyldnConst
#from lib import Receiver

import logging

# Logging
LOG_FORMAT = '%(asctime)-15s [%(levelname)s] (%(module)s.%(funcName)s) %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)

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
        cherrypy.tree.mount(self.rootServer, "/", config=self.config)

        cherrypy.engine.start()

if __name__ == '__main__':
    test = LDNReceiverServer()
    test.start()
