#!/usr/bin/env python
#-*-coding:utf-8-*-
# vim: set filetype=python expandtab tabstop=2 shiftwidth=2 autoindent smartindent:

import cherrypy

RDFNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFSNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
SKOSNS = "http://www.w3.org/2004/02/skos/core#"
SKOSXLNS = "http://www.w3.org/2008/05/skos-xl#"
SKOSDict = {'prefLabel': 'skos:prefLabel', 'altLabel':'skos:altLabel', 
    'Concept':'skos:Concept', 'ConceptScheme':'skos:ConceptScheme', 
    'Collection':'skos:Collection', 
    'OrderedCollection': 'skos:OrderedCollection', 'inScheme':'skos:inScheme',
    'hasTopConcept': 'skos:hasTopConcept', 'topConceptOf':'skos:topConceptOf',
    'hiddenLabel': 'skos:hiddenLabel', 'notation': 'skos:notation', 
    'note':'skos:note', 'changeNote': 'skos:changeNote', 
    'definition': 'skos:definition', 'editorialNote':'skos:editorialNote',
    'example': 'skos:example', 'historyNote': 'skos:historyNote', 
    'scopeNote': 'skos:scopeNote', 'semanticRelation': 'skos:semanticRelation', 
    'broader': 'skos:broader', 'narrower': 'skos:narrower', 
    'related': 'skos:related', 'broaderTransitive':'skos:broaderTransitive', 
    'member': 'skos:member', 'narrowerTransitive': 'skos:narrowerTransitive', 
    'memberList': 'skos:memberList', 'mappingRelation': 'skos:mappingRelation', 
    'broaderMatch': 'skos:broaderMatch', 'narrowerMatch': 'skos:narrowerMatch', 
    'relatedMatch': 'skos:relatedMatch', 'exactMatch':'skos:exactMatch', 
    'closeMatch':'skos:closeMatch', 'uri':'skos:Concept'}
SKOSXLDict = {'Label':'skos-xl:Label', 'literalForm': 'skos-xl:liberalForm', 
    'labelRelation': 'skos-xl:labelRelation', 'prefLabel':'skos-xl:prefLabel',}
PREFIXStr = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
            PREFIX cct: <http://cct.nlc.gov.cn/ns/cct#>
            """

PREFIXCollectionStr = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
            PREFIX cct: <http://cct.nlc.gov.cn/ns/cct#>
            PREFIX nlcspecPN: <http://cct.nlc.gov.cn/PersonalnamesThesaurus#>
            PREFIX nlcspecGN: <http://cct.nlc.gov.cn/GeographicnamesThesaurus#>
            PREFIX nlcspecCN: <http://cct.nlc.gov.cn/CorporatenamesThesaurus#>
            PREFIX nlcspecTN: <http://cct.nlc.gov.cn/TitlenamesThesaurus#>
            PREFIX nlcspecPNS: <http://cct.nlc.gov.cn/PersonalnamesSubjectHeading#>
            PREFIX nlcspecGNS: <http://cct.nlc.gov.cn/GeographicnamesSubjectHeading#>
            PREFIX nlcspecCNS: <http://cct.nlc.gov.cn/CorporatenamesSubjectHeading#>
            PREFIX nlcspecTNS: <http://cct.nlc.gov.cn/TitlenamesSubjectHeading#>
            PREFIX nlcspecSC: <http://cct.nlc.gov.cn/SubjectHeading#>
            PREFIX nlcspecS: <http://cct.nlc.gov.cn/SubjectThesaurus#>
            """
PREFIXDict= {'ccst': "http://hdl.handle.net/2453/ccst/",
             'skos': "http://www.w3.org/2004/02/skos/core#",
             'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
             }

SPARQLREPO = "http://192.168.180.243:3030/sparql/query"
SERVERURI = "192.168.180.243:8080"

# BASEURI should be a property of a thesaurus.
# ???
BASEURI = "http://cct.nlc.gov.cn/Subject/"

GLOBALCONFIG= {'server.socket_host': "0.0.0.0",
     'server.socket_port' : 8080,
     'server.thread_pool' : 10,
    }
APPCONFIG = {
    '/':
    {'log.error_file' :"logs/error.log",
     'log.access_file' : "logs/access.log",
     'log.screen' : True,
     'tools.encode.on' : True,
     'tools.encode.encoding': "utf-8",
     'tools.decode.on': True,
     'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },
     '/media':
    {'tools.staticdir.on':True,
     'tools.staticdir.dir': "/home/jason/workspace/pyldn/pyLDN/src/static",
    },
    '/favicon.ico':
    {'tools.staticfile.on':True,
     'tools.staticfile.filename': "/home/jason/workspace/pyldn/pyLDN/src/static/favicon.ico",
    },
}
