#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import requests
import string
import sys
import urllib

from sys import platform
from pprint import pprint

def defaultify(value,defaultValue):
    if value is None:
        return defaultValue
    return value

def defaultifyMap(theMap,key,defaultValue):
    if key in theMap:
        return theMap[key]
    return defaultValue

imdbHated = ["the","a"]
def imdbHates(queryTerm):
    return queryTerm.lower() in imdbHated

imdbTypes = {
    'Actor':'Actor',
    'Actress':'Actress',
    'Feature':'Feature',
    'Tv Movie': 'TV Movie',
    'Tv Series':'TV Series',
    'Tv Special': 'TV Special',
    'Video':'Video',
    'Video Game':'Video Game'
}

def imdbType(key):
    key = string.capwords(key)
    return defaultifyMap(imdbTypes,key,"")

class Entry:
    widths = [4,16,-1,-1]
    fmt = u"{0:4} {1:16} {2} {3}"
    
    def __init__(self,entry):
        self.entry = entry
        self.details = None

    def __str__(self):
        return Entry.fmt.format(self.getYear(),self.getType(),self.getName(),self.getDetails())

    def affectWidths(self):
        Entry.widths[0] = max(Entry.widths[0],len(self.getYear()))
        Entry.widths[1] = max(Entry.widths[1],len(self.getType()))
        Entry.widths[2] = max(Entry.widths[2],len(self.getName()))
        Entry.widths[3] = max(Entry.widths[3],len(self.getDetails()))

    @staticmethod
    def buildFormat():
        Entry.fmt = u"{{0:{0}}} | {{1:{1}}} | {{2:{2}}} | {{3:{3}}}".format(Entry.widths[0],Entry.widths[1],Entry.widths[2],Entry.widths[3])

    @staticmethod
    def getHeader():
        return Entry.fmt.format("Year","Type","Name","Details")
    
    def getType(self):
        if 'q' in self.entry:
            return imdbType(self.entry['q']);
        else:
            rawDetails = self.getRawDetails().split(",")
            if len(rawDetails):
                return imdbType(rawDetails[0])
        return "";

    def getName(self):
        if 'l' in self.entry:
            return self.entry['l']
        return "";

    def getYear(self):
        if 'y' in self.entry:
            return str(self.entry['y'])
        return "";

    def getRawDetails(self):
        if 's' in self.entry:
            return self.entry['s']
        return "";

    def getDetails(self):
        if self.details == None:
            details = self.getRawDetails().split(",")
            if len(details) > 1:
                if len(imdbType(details[0])):
                    details = details[1:]
                    details[0] = details[0].lstrip()
            self.details = u",".join(details)
        return self.details
            
    
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--verbose',dest='verbose',action='store_true',help='Be verbose');
    parser.add_argument('-vv','--reallyVerbose',dest='reallyVerbose',action='store_true',help='Be verbose');
    parser.add_argument(dest='query',nargs='+',help='query')
    args = vars(parser.parse_args(argv))

    reallyVerbose = args['reallyVerbose']
    verbose = reallyVerbose or args['verbose']
    query = args['query']

    query = [queryTerm.lower() for queryTerm in query if not imdbHates(queryTerm)]
    
    # url = "http://www.imdb.com/xml/find?json=1&xml=0&q={}".format(urllib.quote(' '.join(query)))
    # url = "http://www.omdbapi.com/?{}".format(urllib.quote(' '.join(query)))
    url = "https://v2.sg.media-imdb.com/suggests/{}/{}.json".format(query[0][0],'_'.join(query))

    if verbose:
        print "Performing the following imdb query: {}".format(query)
        print "url:{}".format(url)

    r = requests.get(url, headers={'Accept':'application/json'})
    if r.status_code < 200 or r.status_code > 299:
        raise Exception(r.text)
    else:
        prefix = "imdb${}(".format('_'.join(query))
        responseJson = r.text
        if responseJson.startswith(prefix):
            responseJson = responseJson[len(prefix):len(responseJson)-1]
        
        try:
            response = json.loads(responseJson)
        except Exception,e :
            print responseJson
            raise e

        if reallyVerbose:
            pprint(response)

        typed = []
        untyped = []
        generic = []
        if 'd' in response: 
            for entry in response['d']:
                generic.append(Entry(entry))
                if 'q' in entry:
                    entryName=entry['l']
                    entryType=entry['q']
                    entryYear=defaultifyMap(entry,'y',"????")
                    typed.append(u"{} {:9} {}".format(entryYear,string.capwords(entryType),entryName))
                else:
                    entryName=entry['l']
                    entryExtra=defaultifyMap(entry,'s',"")
                    untyped.append( u"'{}' {}".format(entryName,entryExtra) )

        #print u"\n".join(typed)
        #print u"\n".join(untyped)
        for x in generic:
            x.affectWidths()
        Entry.buildFormat()
        print Entry.getHeader()
        print u"\n".join([unicode(x) for x in generic])

if __name__ == "__main__":
    main(sys.argv[1:])

