#!/usr/bin/env python

import re

def str_to_mac(s):
    p = re.compile("(\d+).(.*)")
    m = p.match(s)
    mac = ""
    if m:
        oc = m.group(2).split(".")
        mac = ""
        for i in oc:
            h = "%x" % int(i)
            if len(h) == 1:
                h = "0"+h
            mac = mac+str.upper(h)+":"
    return mac[:-1]

def pmac(m):
    m = m[2:]
    offset = 0
    mac = ""
    while True:
        o = m[offset:2+offset]
        offset += 2
        if o:
            mac += str.upper(o)+":"
        else:
            break
    return mac[:-1]



