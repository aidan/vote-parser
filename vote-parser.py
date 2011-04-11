#!/usr/bin/env python

import xml.parsers.expat
import re

file = open("/home/aidan/src/vote-parser/data/sp2008-11-19.xml", "r")
party_matcher = re.compile(r".*\((\w+)\)")

divisions = []
this_division = {}
vote = ""
in_msp = False

def start_element(name, attrs):
    global divisions, this_division, vote, in_msp
    if name == "division":
        this_division["id"] = attrs["id"]
    elif name == "msplist":
        vote = attrs["vote"]
        this_division[vote] = {}
    elif name == "mspname":
        in_msp = True

def end_element(name):
    global divisions, this_division, vote, in_msp
    if name == "division":
        divisions.append(this_division)
        this_division = {}
    elif name == "mspname":
        in_msp = False

def char_data(data):
    global divisions, this_division, vote, in_msp
    if in_msp:
        m = party_matcher.match(repr(data))
        if (m):
            party = m.group(1)
            if not party in this_division[vote].keys():
                this_division[vote][party] = 0
            this_division[vote][party] = this_division[vote][party] + 1

def main():
    p = xml.parsers.expat.ParserCreate()
    
    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data
    
    p.ParseFile(file)

    for division in divisions:
        for vote in ["for", "against"]:
            for party in division[vote].keys():
                print ("{0} {1} {2}".format(vote, party, division[vote][party]))
        print("\n")
        
if __name__ == "__main__":
    main()
