'''Namespace'''

from rdflib import Namespace, URIRef
from urlparse import urlparse

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

DELIMITER01 = '/'
DELIMITER02 = '#'
      
def updatens(prefixNS, defaultNS):
   for (prefix, myNSUri) in prefixNS:
      myNSUri = myNSUri.title().lower()
      if myNSUri not in NS:
         if prefix == '':
            NS[myNSUri]=defaultNS
         else:
            NS[myNSUri]=prefix

def updatens1(prefix, nsuri, defaultNS):
   if nsuri not in NS:
      if prefix == '':
         NS[nsuri]=defaultNS
      else:
         NS[nsuri]=prefix
            
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
   
def nsType(seg1, seg2, delimiter):
   retVal = ''
   tmp = seg1 + delimiter
   if (tmp in NS):
      if (seg2 != ''):
         tempChar = seg2[0:1]
         if (tempChar >= 'A' and tempChar <= 'Z'):
            retVal = 'Category'
         else:
            retVal = 'Property'
      else:
         retVal = 'ns??'
   return retVal

def wikitype(uri):
   
   if (type(uri).__name__ == 'BNode'):
      return 'Internal'
   
   # make sure uri is type of URIRef
   if type(uri).__name__ != 'URIRef':
      uri = URIRef(uri)
      
   delimiters01 = uri.rsplit(DELIMITER01,1)
   delimiters02 = uri.rsplit(DELIMITER02,1)
   
   retVal = ''
   if (len(delimiters01) == 1 and (len(delimiters02) == 1)):
      print uri
      retVal = ''
   elif (len(delimiters01) == 2 and (len(delimiters02) == 1)):
      #
      retVal = nsType(delimiters01[0], delimiters01[1], DELIMITER01)

   elif (len(delimiters01) == 1 and (len(delimiters02) == 2)):
      
      retVal = nsType(delimiters02[0], delimiters02[1], DELIMITER02)

   else:
      if (len(delimiters01[0]) > len(delimiters02[0]) ):
         retVal = nsType(delimiters01[0], delimiters01[1], DELIMITER01)
      else:
         retVal = nsType(delimiters02[0], delimiters02[1], DELIMITER02)
         
   '''   
   t = urlparse(uri)
   retVal=''
   if (t.scheme == '' and t.path != ''):
      retVal = ''
   else:
      if (t.fragment != ''):
         tempChar = t.fragment[0:1]
         if (tempChar >= 'A' and tempChar <= 'Z'):
            retVal = 'Category'
         else:
            retVal = 'Property'
         
   #if retVal == '':
      t = striplast(stripns(uri))
      if (t!=''):
         tempChar = t[0:1]
         if (tempChar >= 'A' and tempChar <= 'Z'):
            retVal = 'Category'
         else:
            retVal = 'Property'
   '''         
   return retVal