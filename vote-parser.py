#!/usr/bin/env python
from __future__ import division

import os
import re
import xml.parsers.expat

party_matcher = re.compile(r".*\((\w+)\)")
year_matcher = re.compile(r"sp([0-9][0-9][0-9][0-9])-([0-9][0-9]).*")

divisions = []
this_division = {}
vote = ""
in_msp = False
govt = "LAB"
opposition = "SNP"
years = {}
year = 1999

def start_element(name, attrs):
    global divisions, this_division, vote, in_msp
    if name == "division":
        this_division["id"] = attrs["id"]
    elif name == "msplist":
        vote = attrs["vote"]
        this_division[vote] = {"SNP": 0,
                               "LAB": 0,
                               "CON": 0,
                               "LD": 0,
                               "IND": 0,
                               "GREEN": 0,
                               "GLASGOW": 0,
                               "SSCUP": 0,
                               "SSP": 0}
    elif name == "mspname":
        in_msp = True

def end_element(name):
    global divisions, this_division, vote, in_msp, govt, opposition, years, year
    if name == "division":
        divisions.append(this_division)
        if (this_division["for"][govt] > 10 and this_division["for"]["CON"] > 10
            and this_division["for"][opposition] < 5):
            years[year]["collusion"] = years[year]["collusion"] + 1

        if ("against" in this_division.keys() and this_division["against"][govt] > 10 and this_division["against"]["CON"] > 10
            and this_division["against"][opposition] < 5):
            years[year]["collusion"] = years[year]["collusion"] + 1
            
        years[year]["total"] = years[year]["total"] + 1
        this_division = {}
    elif name == "mspname":
        in_msp = False

def char_data(data):
    global divisions, this_division, vote, in_msp
    if in_msp:
        m = party_matcher.match(repr(data))
        if (m):
            party = m.group(1).upper()
            if not party in this_division[vote].keys():
                this_division[vote][party] = 0
            this_division[vote][party] = this_division[vote][party] + 1
            
def main():
    global divisions, govt, opposition, years, year
    
    for dirname, dirnames, filenames in os.walk('/home/aidan/src/vote-parser/data/'):
        for filename in filenames:
            p = xml.parsers.expat.ParserCreate()
            p.StartElementHandler = start_element
            p.EndElementHandler = end_element
            p.CharacterDataHandler = char_data

            m = year_matcher.match(filename)
            if (m): 
                year = m.group(1)
                if year not in years.keys():
                    years[year] = {"collusion": 0,
                                   "total": 0}
                if int(year) < 2007 and int(m.group(2) < 4):
                    govt = "LAB"
                    opposition = "SNP"
                else:
                    govt = "SNP"
                    opposition = "LAB"
                    
            else:
                print ("No year for "+filename)
                
            file = open('/home/aidan/src/vote-parser/data/'+filename, "r")
            p.ParseFile(file)
            
    for year in years:
        collusion = int(years[year]["collusion"])
        total = int(years[year]["total"])
        if (collusion > 0 and total > 0):
            ratio = (collusion / total) * 100
        else:
            ratio = 0
        print "%s Tories voted with govt %d times of %d or %d%%" % (year,
                                                                    collusion,
                                                                    total,
                                                                    ratio)
        
if __name__ == "__main__":
    main()
