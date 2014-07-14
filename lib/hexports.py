#!/usr/bin/env python

def hex_to_ports(hex_str):
    offset = 0
    bin_str = ""
    ports = []
    while True:
        h = hex_str[offset:1+offset]
        offset += 1
        b = ""
        if h:
            b = str(bin(int(h.lower(), 16)))[2:]
            if len(b)<4:
                b = "0"*(4-len(b))+b
            bin_str += b
        else:
            break
    for i in xrange(0, len(bin_str)):
        if bin_str[i] == str(1):
            ports.append(i+1)
    return ports



