#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telnetlib
import re
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902

RO_COMM = "public"
RW_COMM = "private"

class SNMP():
    def __init__(self, ip):
        self.ip = str(ip)
        self.ro = RO_COMM
        self.rw = RW_COMM
        self.generator = cmdgen.CommandGenerator()
        self.read_comm = cmdgen.CommunityData('server', self.ro, 1)
        self.write_comm = cmdgen.CommunityData('server', self.rw, 1)
        self.transport = cmdgen.UdpTransportTarget((self.ip, 161))
    def get(self, oid):
        errorIndication, errorStatus, errorIndex, varBinds = self.generator.getCmd(
                self.read_comm,
                self.transport,
                oid
        )
        if not errorIndication is None  or errorStatus is True:
            raise RuntimeError("Какая то хуйня с SNMP на свиче %s" % self.ip)
        else:
            r = varBinds[0][1].prettyPrint()
            if r != "No Such Instance currently exists at this OID":
                return r
            else:
                return None
    def set(self, oid, val):
        def get_type(v):
            ip_re = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
            t = ""
            if isinstance(v, int):
                t = rfc1902.Integer(v)
            elif isinstance(v, basestring):
                if ip_re.match(v):
                    t = rfc1902.IpAddress(v)
                else:
                    t = rfc1902.OctetString(v)
            return t

        errorIndication, errorStatus, errorIndex, varBinds = self.generator.setCmd(
                self.write_comm,
                self.transport,
                (oid, get_type(val))
        )
        if not errorIndication is None or errorStatus is True:
            raise RuntimeError("Какая то хуйня с SNMP на свиче %s" % self.ip)
        else:
            return True

    def walk(self, oid):
        p = re.compile(oid+".(.*)")
        resp = {}
        errorIndication, errorStatus, errorIndex, varBindTable = self.generator.nextCmd(
            self.read_comm,
            self.transport,
            oid
        )
        if not errorIndication is None  or errorStatus is True:
            pass
        else:
            for varBindTableRow in varBindTable:
                for name, val in varBindTableRow:
                    k = name.prettyPrint()
                    v = val.prettyPrint()
                    resp[p.match(k).group(1)] = v
        return resp
