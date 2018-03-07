'''Namespace'''

from rdflib import Namespace

RDF=Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS=Namespace('http://www.w3.org/2000/01/rdf-schema#')
DC=Namespace('http://purl.org/dc/elements/1.1/')
DCTERMS=Namespace('http://purl.org/dc/terms/')
DCTYPE=Namespace('http://purl.org/dc/dcmitype/')
DCAM=Namespace('http://purl.org/dc/dcam/')
SKOS=Namespace('http://www.w3.org/2004/02/skos/core#')
CST=Namespace("http://libnt2.lakeheadu.ca:8080/cst/")
      
NS={}
NS[RDF.title().lower()] = 'rdf'
NS[RDFS.title().lower()] = 'rdfs'
NS[DC.title().lower()] = 'dc'
NS[DCTERMS.title().lower()] = 'dcterms'
NS[DCTYPE.title().lower()] = 'dctype'
NS[DCAM.title().lower()] = 'dcam'
NS[SKOS.title().lower()] = 'skos'
      
def updatens(prefixNS, defaultNS):
   for (prefix, myNSUri) in prefixNS:
      if myNSUri not in NS:
         if prefix == '':
            NS[myNSUri]=defaultNS
         else:
            NS[myNSUri]=prefix
            
def stripns(str):
   for k,v in NS.items():
      str=str.replace(k,v+':')
   return str
      
def striplast(str):
   pos=-1
   pos = str.find(':')
   if pos>=0:
      pos=pos+1
   else:
      pos=0
   return str[pos:]

def uniq(alist):
   s=set(alist)
   return list(s)

def uniqa(alist):
   return dict.fromkeys(alist).keys()
