#!/usr/bin/env python

from lib import interface
from lib import models
import re


class Switch(object):
    def __init__(self, ip):
        self.ip = ip
        self.snmp = interface.SNMP(self.ip)
        self.sysdescr = self.snmp.get(".1.3.6.1.2.1.1.1.0")
        if self.sysdescr:
            self.short_model = self.short_model()
            self.model = models.get(self.short_model)
            if self.model:
                self.action = self.model(self)
    def short_model(self):
        switch_patern = ".*(DES|DGS)-(\d{4}){1}-?(\d{2})?\/?(\S{1,2})?.*"
        p = re.compile(switch_patern)
        m = p.match(str(self.sysdescr))
        sm = ""
        if m:
            sm = str(m.group(1))+str("_")+str(m.group(2))
            if m.group(3):
                sm += str("_")+str(m.group(3))
            if m.group(4):
                sm += str("_")+str(m.group(4))

        return sm


