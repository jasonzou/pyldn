#!/usr/bin/env python
#-*-coding:utf-8-*-
# vim: set filetype=python expandtab tabstop=2 shiftwidth=2 autoindent smartindent:

import cherrypy
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import urlparse
from cherrypy.lib import httputil
from lib import cct2Templ

from cherrypy.lib.cptools import accept
import pprint

from rdflib import *
import sys

import simplejson                                                              
import rdflib

#import pydot
#import ipaddr

from lib import pyldnConst

import time
"""
----------------------------------------
Author: Qing Zou <jason.zou@gmail.com>
Created: May 6, 2011
Last Modified: May 17, 2011
=======================================
To-do list:
     1. Catch Exceptions 
     2. Add test cases (unittest)
---------------------------------------
"""


def error_page_404(status, message, traceback, version):
    templ = cct2Templ.loader.load('cct2http404.html')
    stream = templ.generate(status=status,message=message)
    return stream.render('xhtml')
    #return "Error %s - Well, I'm very sorry." % status

def error_page_405(status, message, traceback, version):
    templ = cct2Templ.loader.load('cct2http405.html')
    stream = templ.generate(status=status,message=message)
    return stream.render('xhtml')

def error_page_500(status, message, traceback, version):
    templ = cct2Templ.loader.load('cct2http500.html')
    stream = templ.generate(status=status,message=message)
    return stream.render('xhtml')

def handle_error():
    cherrypy.response.status = 500
    templ = cct2Templ.loader.load('cct2http500.html')
    stream = templ.generate(status=500,message="Internal Server Error, please contact the site administrator jason.zou@gmail.com. ")
    response = stream.render('xhtml')
    cherrypy.response.body = [response]

def stripNS(uri):
    internalURI = uri
    for item, value in PREFIXDict.iteritems():
        internalURI = internalURI.replace(value, item+":")
    return internalURI

def log(str, level=2):
    # 0 - info
    # 1 - warning
    # 2 - error
    if level > 2:
       cherrypy.log(str)
       level = level

class CCST(object):
    _cp_config = {
        'tools.encode.on':True,
        'tools.encode.encoding':'utf-8'}
    def __init__(self, content=None, tmpl='ccst'):
        self.content = content
        self.tmpl = tmpl
        self.base = BASEURI + tmpl
        self.descList = []
        self.prefix = tmpl
        self.wadlDesc = ''
    
    def getWADLDescription(self):
        self.wadlDesc = self.OPTIONS(self.id)
        
    def description(self):
        qStr = pyldnConst.PREFIXStr + """PREFIX kos: <http://hdl.handle.net/2453/kos/>
            SELECT ?p ?o
            WHERE { kos:%s ?p ?o }
            ORDER BY ?p
        """ % (self.prefix)
        
        log(qStr)
        sparqlDesc = SPARQLWrapper(pyldnConst.SPARQLREPO)
        sparqlDesc.setQuery(qStr)
        sparqlDesc.setReturnFormat(JSON)
        descs = sparqlDesc.queryAndConvert()
        
        self.descList = []

        for desc in descs["results"]["bindings"]:
            templist = {}
            templist['property'] = desc["p"]["value"]
            templist['value'] = desc["o"]["value"]
            self.descList.append(templist)
            log(str(templist))

    def ipDeny(self):
        """access control by using ip address"""
        return False
        allowList = ['221.237.0.0/16', '192.168.0.0/16','174.5.0.0/16']
        requestIp = ipaddr.IPv4Address(cherrypy.request.remote.ip)
        for tempNet in allowList:
            allowNet = ipaddr.IPv4Network(tempNet)
            if requestIp in allowNet:
                return False
        return True

    exposed = True
    def index(self):
        return "Things galore!"

    exposed = True
    _cp_dispatch = cherrypy.popargs('id') 
    def GET(self, id=None, *args, **kwargs):
        if len(args) > 1:
           #test = self.doQuery(self.id)
           #return test
           raise cherrypy.HTTPError(405, "Not Supported! %d " % len(args))
        
        conceptid = unicode(str(id), "utf-8")
        self.id = conceptid
        log("============= id => %s" % self.id)
                
        if self.id == 'None':
           self.id = ''

        if self.ipDeny():
            raise cherrypy.HTTPError(403, "Not Supported!")
        else:
            if len(kwargs) >= 1:
                for key in kwargs:
                    log("params (%s, %s) " % (key,kwargs[key]))
                raise cherrypy.HTTPError(405, "Not Supported - attributes! -> %s" % self.id)
            else:
                best = accept(['application/rdf+xml', 'text/json', 
                       'text/x-json', 'text/html', 'application/rdf', 'application/xml'])
                log(str(best))
                

                if best  in ['text/json', 'text/x-json']:
                    self.format = 'json'
                elif best in ['text/html']:
                    self.format = 'html'
                elif best in ['application/rdf', 'application/rdf+xml']:
                    self.format = 'rdf'
                concept = Concept(id=self.id, format=self.format)
                self.getWADLDescription()
                return concept.result(self.descList, self.wadlDesc)
                        
    def json(self):
        return "<html> JSON </html>"
    
    def rdf(self):
        return "<html> RDF </html>"

    exposed = True
    def PUT(self):
        raise cherrypy.HTTPError(405, "Not Supported!")
    
    exposed = True
    _cp_dispatch = cherrypy.popargs('id') 
    def OPTIONS(self, id=None, *args, **kwargs):
        if id == None:
            self.id = '/'
            tmpl = self.tmpl+'wadlDesc.xml'
            templ = cct2Templ.loader.load(tmpl)
            stream = templ.generate(conceptId=self.id)
            return stream.render('xml')
        else:
            conceptid = unicode(str(id), "utf-8")
            self.id = conceptid
            
            temp = quickES(self.id)
            tempValue = temp.getValue()
            if tempValue != None:
                log("OPTIONS")
                tmpl = self.tmpl+'wadlDesc.xml'
                templ = cct2Templ.loader.load(tmpl)
                stream = templ.generate(conceptId=self.id)
                return stream.render('xml')
        #self.searchHtml()
        #self.content = self.from_html(cherrypy.request.body.read())
        # return wadl description

    def html(self):
        tmpl = self.tmpl+'Index.html'
        templ = cct2Templ.loader.load(tmpl)

        self.description()
        if len(self.descList) == 0:
            stream = templ.generate(descs={})
        else:
            stream = templ.generate(descs=self.descList)
        self.descList = []
        return stream.render('xhtml')
    
    
    def __getattr__(self, name):
        log("==== restful -> %s" % name)
        if name.isdigit():
            cherrypy.request.params['thingid'] = name
            return self.default
        raise AttributeError("%r object has no attribute %r" % (self.__class__.__name__, name))

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
        log('enter Root - Get')
        
        log("vis is 1" )
        #json = []
        #mainNodes = self.getQClass()
        mainNodes = [] 
        request = cherrypy.serving.request
        req_h = request.headers
        print(req_h)

        resp_h = cherrypy.serving.response.headers
        resp_h['X-Powered-By']='http://nkos.info'
        cherrypy.response.header_list = [("Content-Type", 'text/html'),
                                         ("Server", "Null CherryPy"),
                                         ("Content-Length", "0"),
                                         ]
        cherrypy.response.body = ['']
        return cherrypy.response

        #return print(request)
        
        #log("vis is 2" + mainNodes)
        #mainNodes = []
        #self.description()
        templStr = self.prefix+"Index.html"
        templ = cct2Templ.loader.load(templStr)
        elapsedTime = time.time() - self.startime

        self.descList = []
        stream = templ.generate()
        return stream.render('xhtml')
    
    def internalURI(self, uri):
        tempUri = urlparse(uri)
        retStr = ""
        if tempUri.scheme == 'http' and tempUri.netloc != '':
            if tempUri.netloc == 'cct.nlc.gov.cn' or tempUri.netloc == "id_cct-heading.nlc.gov.cn":
                newLoc = pyldnConst.SERVERURI
                newPath = tempUri.path #.replace("Subject", "cct2/concept")
                newURI = str(tempUri.scheme)+"://"+newLoc+newPath+"#"+str(tempUri.fragment)
                #retStr = '<a href="%s">%s</a>' %(newURI, uri)
                retStr = newURI
            else:
                #retStr = '<a href="%s">%s</a>' %(uri, uri)
                retStr = uri
        else:
            retStr = uri
        return retStr
    
    def merge(lsta, lstb):
        for i in lstb:
            for j in lsta:
                if j['name'] == i['name']:
                    j.update(i)
                    break
                else:
                    lsta.append(i)


    
    def getURIId(self, str):
        tempUri = urlparse(str)
        log('-------33334444 %s ' % str)
        log('-------33334444 %s ' % tempUri.path)
        return tempUri.path.replace('/Subject/','')
    
    def getCollectionsInfo(self):
        qStr = pyldnConst.PREFIXStr + """
            SELECT DISTINCT ?collection ?title (count(?value) as ?count) WHERE {
                ?collection rdf:type skos:OrderedCollection;
                    skos:prefLabel ?title;
                    skos:member ?value.
            }
            GROUP BY ?collection ?title
            """
        log(qStr)
        sparqlDesc = SPARQLWrapper(pyldnConst.SPARQLREPO)
        sparqlDesc.setQuery(qStr)
        sparqlDesc.setReturnFormat(JSON)
        descs = sparqlDesc.queryAndConvert()
        
        nodeList = []
        json = {}
        
        # go through all the triples in the graph
        
                
        for result in descs["results"]["bindings"]:
            mainNode={}
            mainNode['name'] = result["title"]["value"]
            mainNode['link'] = self.internalURI(result["collection"]["value"])
            mainNode['size'] = result["count"]["value"]
            log('main node --- ' + str(mainNode))
                       
            nodeList.insert(0, mainNode)
        
        
        json['name'] = "CCT2 Collections"
        json['children'] = nodeList


        log("vis is " + simplejson.dumps(json))
        return simplejson.dumps(json)

class notImplemented(object):
    _cp_config = {'request.error_response': handle_error,
        'tools.encode.on':True,
        'tools.encode.encoding':'utf-8'}
    def __init__(self, name="cct2"):
        self.prefix = name
        self.descList = []
     
    exposed = True
    def GET(self):
        log('enter notImplemented - Get')
        
        #self.description()
        templStr = self.prefix+"IndexNotImplemented.html"
        templ = cct2Templ.loader.load(templStr)
        stream = templ.generate(descs=self.descList,json=json)
        return stream.render('xhtml')
       
class CCTConcept(object):
    def __init__(self, conceptid, item=None):
        self.item = item
        self.conceptId = conceptid
        self.index = 'cct'
        
        self.json = None
        self.jsonObj = None
        self._getJSONById()
        
        try:
            self.jsonObj = json.loads(self.json.replace('\x00', '').replace('\x80','').replace('\r','').replace('\n', ''))
        except Exception:
            pass
        

    def _getJSONById(self):
        try:
            #code
            temp = self.item
            self.json = json.dumps(temp)
        except Exception:
            # exception handling 
            pass
    
    def getId(self):
        return self.conceptId
    
    def _getPrefLabel(self, lang = "zh"):
        retVal = None
        try:
            if self.jsonObj.has_key("skosxl:literalForm"):
                ret = self.jsonObj["skosxl:literalForm"]
            else:
                ret = self.jsonObj["skos:prefLabel"]
            retVal = None
            for item in ret:
                if item["@language"] == lang:
                    retVal = item["@value"]
            
        except Exception:
            pass
        return retVal

    def _getAltLabel(self, lang = "zh"):
        retVal = None
        try:
            retVal = None
            if lang=="zh-pinyin":
                if self.jsonObj.has_key("cct:transliteration"):
                    ret = self.jsonObj["cct:transliteration"]
                    retVal = ret["@value"]
                else:
                    ret = self.jsonObj["skos:altLabel"]
                    for item in ret:
                      if item["@language"] == lang:
                         retVal = item["@value"]
            if lang == "zh":
                if self.jsonObj.has_key("skosxl:literalForm"):
                    ret = self.jsonObj["skosxl:literalForm"]
                    retVal = ret["@value"]
                else:
                    ret = self.jsonObj["skos:altLabel"]
                    for item in ret:
                      if item["@language"] == lang:
                         retVal = item["@value"]
                
            
        except Exception:
            pass
        return retVal
    
    def hasXLAltLabel(self):
        retVal = False
        try:
            ret = self.jsonObj["skosxl:altLabel"]
            retVal = True
        except Exception:
            pass
        return retVal
    
    
    
    def getPrefLabelChn(self):
        return self._getPrefLabel()
    
    def getPrefLabelPinyin(self):
        return self._getPrefLabel(lang="zh-pinyin")

    def getPrefLabelEng(self):
        return self._getPrefLabel(lang="en")

    def getAltLabelChn(self):
        return self._getAltLabel()
        
    def getAltLabelPinyin(self):
        return self._getAltLabel(lang="zh-pinyin")
        
    
        
    def internalURI(self, uri):
        tempUri = urlparse(uri)
        retStr = ""
        if tempUri.scheme == 'http' and tempUri.netloc != '':
            if tempUri.netloc == 'cct.nlc.gov.cn' or tempUri.netloc == "id_cct-heading.nlc.gov.cn":
                newLoc = ''
                newPath = tempUri.path.replace("/Subject/", "")
                #newURI = str(tempUri.scheme)+"://"+newLoc+newPath+"#"+str(tempUri.fragment)
                #retStr = '<a href="%s">%s</a>' %(newURI, uri)
                retStr = newPath
            else:
                #retStr = '<a href="%s">%s</a>' %(uri, uri)
                retStr = uri
        else:
            retStr = uri
        return retStr
    
    def getJSON(self, cctid):
        self.queryStr = PREFIXStr + """
            CONSTRUCT { <%s> ?p ?o } WHERE {
                <%s> ?p ?o
            } 
            """ % (cctid, cctid)
        self.sparql.setQuery(self.queryStr)
        self.sparql.setReturnFormat(format='xml')
        results = self.sparql.query().convert()
        
        g=Graph()
        g.bind('skos', SKOSNS)
        g.bind('skosxl', SKOSXLNS)
        g.bind('rdf', RDFNS)
        g.namespace_manager.bind('skos', URIRef(SKOSNS))
        g.namespace_manager.bind('skosxl', URIRef(SKOSXLNS))
        g.namespace_manager.bind('rdf', URIRef(RDFNS))
        for stmt in results:
            g.add(stmt)
        g.commit()
        
        #retStr = g.serialize(format='n3')

        #print retStr
        #g = rdflib.ConjunctiveGraph()
        #g.parse(ttl, format='n3')
        #print g.serialize(None,format='json-ld', ident=4)

        context = {"skos": "http://www.w3.org/2004/02/skos/core#",
           "cct": "http://cct.nlc.gov.cn/Subject#",
           "skosxl": SKOSXLNS,
           "rdf": RDFNS}
        test=g.serialize(None,format='json-ld',context=context, ident=4)
        
        

        if self.conn:
            self.conn.index(test, 'cct', 'label', id=self.internalURI(cctid))
            self.conn.indices.refresh('cct')

class CCTSearch(object):
    def __init__(self):
        #self.conn = Elasticsearch()
        self.conn = ES(['127.0.0.1:9200'])
        self.index = "cct"
        #self.query = query
        #app.logger.info(query)
    
    exposed = True
    def index(self):
        return "test jjjason"
    
    _cp_dispatch = cherrypy.popargs('id')
    def GET(self, id=None, *args, **kwargs):

        log("-- ES Search::GET ---- ")

        if len(args) > 1:
           #test = self.doQuery(self.id)
           #return test
           raise cherrypy.HTTPError(405, "Not Supported! %d " % len(args))
        else:
           if len(kwargs) >= 1:
              self.id = kwargs['search']
              self.searchOption = kwargs['searchOption']
              log("ip =====" + self.searchOption)

              self.direction = 'searchAll'
              #raise cherrypy.HTTPRedirect('/cct2/concepts/%s.all' % self.id)
              test = self.search(self.id)
              return test
           else:
              test = self.search(self.id)
              #raise cherrypy.HTTPError(405, "Not Supported - normal! )%s" % self.id)
              if self.format == 'html':
                 test1 = '<html><head><title>terminology web service</title></head><body>%s </body></html>' % (test)
              else:
                 test1 = test
              return test
            
    def search(self, query):
        #q=TextQuery("_all", query, type="phrase")
        q=MatchQuery("_all", query, type="phrase")
        #s=Search(q)
        resultSet = self.conn.search(query=q, index=self.index)
        myresult = []
        
        id=0
        zh=''
        for item in resultSet:
            id = item._meta.id
            
            tempConcept = CCTConcept(id, item)
            
            if tempConcept.getPrefLabelChn():
                
                zh = tempConcept.getPrefLabelChn()
                pinyin = tempConcept.getPrefLabelPinyin()
            else:
                
                zh = tempConcept.getAltLabelChn()
                pinyin = tempConcept.getAltLabelPinyin()
            
            #if zh != None:
            #log("resulttt =====> " + id)
            #log("resulttt =====> " + zh)
            myresult.append(link(id, pinyin,zh))
        
        templ = cct2Templ.loader.load('record.html')
        stream = templ.generate(links=self.orderedList(myresult), keyword=query)
        return stream.render("xhtml",doctype="xhtml")
        #return ""
    
    def orderedList(self,myResult):
        ordered = {}
        pinyinList = []
        for item in myResult:
            pinyinList.append(item.predicate)
            ordered[item.predicate] = item
        tempOrderList = sorted(pinyinList)
        newList = []
        for item in tempOrderList:
            newList.append(ordered[item])
        return newList
    
def receiver(): 
    """Start with the builtin server.""" 
    # Set up site-wide config. Do this first so that, 
    # if something goes wrong, we get a log. 
    log(cherrypy.request.remote.ip)
    log("+++++++++ ip ++++++++++++")

    root = Thesaurus('pyldn')

    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.config.update({'error_page.405': error_page_405})
    cherrypy.config.update({'error_page.500': error_page_500})

    cherrypy.config.update(pyldnConst.GLOBALCONFIG) 
    cherrypy.tree.mount(root, "/", config=pyldnConst.APPCONFIG)
   
    #log(str(cherrypy.config["tools.encode.on"]))
    #log(cherrypy.config["tools.encode.encoding"])
    

    #cherrypy.server.quickstart() 
    cherrypy.engine.start() 

if __name__ == "__main__": 
    receiver() 

