#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import argparse
import fnmatch
import json
import os
import pyperclip
import requests
import string
import sys
import unicodedata
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
    widths = [5,4,16,-1,-1,-1]
    fmt = u"{0:4} {1:16} {2} {3} {4} {5}"
    index = -1
    
    def __init__(self,entry):
        self.entry = entry
        self.details = None

    def __str__(self):
        return Entry.fmt.format(self.getIndex(),self.getYear(),self.getType(),self.getName(),self.getDetails(),self.getPlex())

    def affectWidths(self):
        Entry.widths[0] = max(Entry.widths[0],len("{}".format(self.getIndex())))
        Entry.widths[1] = max(Entry.widths[1],len(self.getYear()))
        Entry.widths[2] = max(Entry.widths[2],len(self.getType()))
        Entry.widths[3] = max(Entry.widths[3],len(self.getName()))
        Entry.widths[4] = max(Entry.widths[4],len(self.getDetails()))
        Entry.widths[5] = max(Entry.widths[5],len(self.getPlex()))

    @staticmethod
    def buildFormat():
        Entry.fmt = u"{{0:<{0}}} | {{1:{1}}} | {{2:{2}}} | {{3:{3}}} | {{4:{4}}} | {{5:{5}}}".format(max(1,Entry.widths[0]),max(1,Entry.widths[1]),max(1,Entry.widths[2]),max(1,Entry.widths[3]),max(1,Entry.widths[4]),max(1,Entry.widths[5]))

    @staticmethod
    def getHeader():
        return Entry.fmt.format("Index","Year","Type","Name","Details","Plex Name")
    
    def getType(self):
        if 'q' in self.entry:
            return imdbType(self.entry['q']);
        else:
            rawDetails = self.getRawDetails().split(",")
            if len(rawDetails):
                return imdbType(rawDetails[0])
        return "";

    def getExtendedPlex(self):
        return u"{} ({}).mkv  {}".format(self.getPlexName(),self.getYear(),self.getDetails())

    def getPlex(self):
        return u"{} ({}).mkv".format(self.getPlexName(),self.getYear())

    def getPlexName(self):
        temp = self.getName()
        temp = unicodedata.normalize('NFKD',temp).encode('ascii','ignore')
        temp = temp.replace(':'," - ")
        temp = temp.replace('&',"-")
        temp = temp.replace('!',"")
        temp = temp.replace("'","")
        temp = temp.replace("\t"," ")
        temp = temp.replace("\r"," ")
        temp = temp.replace("\n"," ")
        temp = temp.replace("  "," ")
        if temp.startswith("The "):
            temp = temp[4:]
        if temp.startswith("A "):
            temp = temp[2:]
        if temp.startswith("An "):
            temp = temp[3:]
        return temp

    def getIndex(self):
        return self.index;

    def setIndex(self, value):
        self.index = value;
    
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
            
    
def main():
    argv = sys.argv
    parser = argparse.ArgumentParser(argv[0])
    parser.add_argument('-f','--filter',dest='include',nargs='*',default=['feature','video','tv series','tv movie','tv special'],help='Include Glob Filter');
    parser.add_argument('-i','--index',dest='copyIndex',type=int,default=0,help='Index to copy [-1 to disable]');
    parser.add_argument('-p','--plex',dest='plex',action='store_true',help='Print in plex format'); 
    parser.add_argument('-v','--verbose',dest='verbose',action='store_true',help='Be verbose');
    parser.add_argument('-vv','--reallyVerbose',dest='reallyVerbose',action='store_true',help='Be verbose');
    parser.add_argument(dest='query',nargs='+',help='query')
    args = vars(parser.parse_args(argv[1:]))

    reallyVerbose = args['reallyVerbose']
    verbose = reallyVerbose or args['verbose']
    query = args['query']
    copyIndex = args['copyIndex']
    includes = args['include']

    query = [queryTerm.lower() for queryTerm in query if not imdbHates(queryTerm)]
    
    # url = "http://www.imdb.com/xml/find?json=1&xml=0&q={}".format(urllib.quote(' '.join(query)))
    # url = "http://www.omdbapi.com/?{}".format(urllib.quote(' '.join(query)))
    url = "https://v2.sg.media-imdb.com/suggests/{}/{}.json".format(query[0][0],'_'.join(query))

    if verbose:
        print "Performing the following imdb query: {}".format(query)
        print "url:{}".format(url)
        print "Using the following filters: {}".format(includes)

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

        entries = []
        if 'd' in response: 
            for e in response['d']:
                entry = Entry(e)
                for pattern in includes:
                    if fnmatch.fnmatch(entry.getType().lower(),pattern.lower()):
                        entries.append(entry)

        if args['plex']:
            for x in entries:
                print x.getExtendedPlex()
        else:
            index = 0
            for x in entries:
                x.setIndex(index)
                index += 1
            for x in entries:
                x.affectWidths()
            Entry.buildFormat()
            print Entry.getHeader()
            print u"\n".join([unicode(x) for x in entries])

        if len(entries) >= copyIndex + 1:
            pyperclip.copy(entries[copyIndex].getPlex())


if __name__ == "__main__":
    main()

