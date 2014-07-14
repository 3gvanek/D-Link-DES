#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from hexports import hex_to_ports
from macstr import str_to_mac, pmac
import time

class Switch(object):
    def __init__(self, switch):
        self.snmp = switch.snmp
class Dlink(Switch):
    pass
class DES(Dlink):
    def portdescr(self, port):
        descr = self.snmp.get(".1.3.6.1.2.1.31.1.1.1.18."+str(port))
        return descr
    def operstatus(self, port):
        st = None
        oper = self.snmp.get(".1.3.6.1.2.1.2.2.1.8."+str(port))
        if oper == "1": st = "Up"
        if oper == "2": st = "Down"
        return st
    def adminstatus(self, port):
        st = None
        oper = self.snmp.get(".1.3.6.1.2.1.2.2.1.7."+str(port))
        if oper == "1": st = "Up"
        if oper == "2": st = "Down"
        return st
    def speed(self, port):
        speed = self.snmp.get(self.l2mgmt+self.portspeed+str(port)+self.speed_add)
        return self.speed_dict.get(speed, None)
    def addrlearn(self, port):
        learn = self.snmp.get(self.l2mgmt+self.learn+str(port)+self.learn_add)
        st = None
        if learn == "2": st = "Disabled"
        if learn == "3": st = "Enabled"
        return st
    def err_disabled(self, port):
        err = self.snmp.get(self.l2mgmt+self.porterr+str(port))
        return self.porterr_dict.get(err, None)
    def errors(self, port):
        errors = {}
        errors['in'] = self.snmp.get(".1.3.6.1.2.1.2.2.1.14."+str(port))
        errors['out'] = self.snmp.get(".1.3.6.1.2.1.2.2.1.20."+str(port))
        return errors
    def cablediag(self, port):
        result = {}
        res_dict = {"0": "Ok", "1": "Open", "2": "Short", "3": "Open-short", "4": "Crosstalk", "5": "Unknown", "6": "Count", "7": "No cable", "8": "Other"}
        start = self.snmp.set(".1.3.6.1.4.1.171.12.58.1.1.1.12."+str(port), 1)
        status = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.13."+str(port))
        while status == "2":
            time.sleep(0.5)
            status = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.13."+str(port))
        if status == "3":
            pair1 = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.4."+str(port))
            pair2 = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.5."+str(port))
            pair3 = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.6."+str(port))
            pair4 = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.7."+str(port))
            dist1 = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.8."+str(port))
            dist2 = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.9."+str(port))
            dist3 = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.10."+str(port))
            dist4 = self.snmp.get(".1.3.6.1.4.1.171.12.58.1.1.1.11."+str(port))
            result["pair1"] = res_dict[pair1]
            result["pair2"] = res_dict[pair2]
            result["pair3"] = res_dict[pair3]
            result["pair4"] = res_dict[pair4]
            result["dist1"] = dist1
            result["dist2"] = dist2
            result["dist3"] = dist3
            result["dist4"] = dist4
            result["diag"] = "Ok"
        if status == "4":
            result["diag"] = "Error"
        return result
    def portfdb(self, port):
        macs = []
        mac_table = self.snmp.walk("1.3.6.1.2.1.17.7.1.2.2.1.2")
        for k, v in mac_table.iteritems():
            if v == str(port):
                macs.append(str_to_mac(k))
        return macs
    def addr_bind(self, port):
        binds = []
        bind_table = self.snmp.walk("1.3.6.1.4.1.171.12.23.4.1.1.4")
        for k, v in bind_table.iteritems():
            ports = hex_to_ports(v[2:])
            if int(port) in ports:
                mac = self.snmp.get("1.3.6.1.4.1.171.12.23.4.1.1.2."+k)
                lease = self.snmp.get("1.3.6.1.4.1.171.12.23.4.3.1.3."+k)
                state = self.snmp.get("1.3.6.1.4.1.171.12.23.4.3.1.5."+k)
                st = None
                if state == "1": st = "Inactive"
                if state == "2": st = "Active"
                binds.append((pmac(mac),k,lease,st))
        return binds

    def addr_block(self, port):
        blocked = []
        block_table = self.snmp.walk("1.3.6.1.4.1.171.12.23.4.2.1")
        p = re.compile("(\d+).(.*)")
        for k, v in block_table.iteritems():
            m = p.match(k)
            if m:
                i = m.group(1)
                if i == "4":
                    if int(port) == int(v):
                        blocked.append(str_to_mac(m.group(2)))
        return blocked
    def mcast_profile(self, port):
        profiles = self.snmp.walk(self.mcast_profiles)
        p = self.snmp.walk(self.mcast_ports)
        for k, v in p.iteritems():
            if "." in k:
                pr = k.split(".")[0]
            else:
                pr = k
            if pr == str(port):
                return profiles.get(v, None)
    def mcast_groups(self, port):
        groups = []
        p = re.compile("\d+.(\d+.\d+.\d+.\d+).*")
        group_table = self.snmp.walk(self.mcast_gr)
        for k, v in group_table.iteritems():
            m = p.match(k)
            if m:
                if v == str(port):
                    groups.append(m.group(1))
                if len(v) > 2:
                    ports = hex_to_ports(v[2:])
                    if ports:
                        if str(ports[0]) == str(port):
                            groups.append(m.group(1))
        return groups

class DES_3200_C1(DES):
    def __init__(self, *args):
        self.portspeed = ".3.1.1.6."
        self.speed_add = ".1"
        self.speed_dict = {"3": "10-Half", "4": "10-Full", "5": "100-Half", "6": "100-Full"}
        self.learn = ".3.2.1.7."
        self.learn_add = ".1"
        self.porterr = ".3.7.1.4."
        self.porterr_dict = {"1": "Loop", "2": "Storm"}
        self.mcast_profiles = "1.3.6.1.4.1.171.12.53.1.1.2"
        self.mcast_ports = "1.3.6.1.4.1.171.12.53.3.1.2"
        self.mcast_gr = "1.3.6.1.4.1.171.12.73.2.1.5.1.3"
        super(DES_3200_C1, self).__init__(*args)

class DES_3200(DES):
    def __init__(self, *args):
        self.portspeed = ".2.1.1.5."
        self.speed_add = ".100"
        self.speed_dict = {"2": "10-Half", "3": "10-Full", "4": "100-Half", "5": "100-Full"}
        self.learn = ".2.2.1.7."
        self.learn_add = ".100"
        self.porterr = ".2.3.1.4."
        self.porterr_dict = {"2": "Storm", "4": "Loop"}
        self.mcast_profiles = self.l2mgmt+".22.2.1.2"
        self.mcast_ports = self.l2mgmt+".22.5.1.2"
        self.mcast_gr = self.l2mgmt+".7.13.1.3"
        super(DES_3200, self).__init__(*args)

class DES_3000(DES):
    def __init__(self, *args):
        self.portspeed = ".2.1.1.5."
        self.speed_add = ".100"
        self.speed_dict = {"2": "10-Half", "3": "10-Full", "4": "100-Half", "5": "100-Full"}
        self.learn = ".2.2.1.7."
        self.learn_add = ".100"
        self.porterr = ".2.3.1.4."
        self.porterr_dict = {"1": "Loop", "2": "Storm"}
        self.mcast_profiles = self.l2mgmt+".22.2.1.2"
        self.mcast_ports = self.l2mgmt+".22.5.1.2"
        self.mcast_gr = self.l2mgmt+".7.5.1.4"
        super(DES_3000, self).__init__(*args)

class DES_3200_10_C1(DES_3200_C1):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.113.2.1.2"
        super(DES_3200_10_C1, self).__init__(*args)

class DES_3200_18_C1(DES_3200_C1):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.113.3.1.2"
        super(DES_3200_18_C1, self).__init__(*args)

class DES_3200_26_C1(DES_3200_C1):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.113.4.1.2"
        super(DES_3200_26_C1, self).__init__(*args)

class DES_3200_28_C1(DES_3200_C1):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.113.5.1.2"
        super(DES_3200_28_C1, self).__init__(*args)

class DES_3200_10(DES_3200):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.113.1.1.2"
        super(DES_3200_10, self).__init__(*args)

class DES_3200_18(DES_3200):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.113.1.2.2"
        super(DES_3200_18, self).__init__(*args)

class DES_3200_26(DES_3200):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.113.1.5.2"
        super(DES_3200_26, self).__init__(*args)

class DES_3200_28(DES_3200):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.113.1.3.2"
        super(DES_3200_28, self).__init__(*args)

class DES_3028(DES_3000):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.63.6.2"
        super(DES_3028, self).__init__(*args)

class DES_3052(DES_3000):
    def __init__(self, *args):
        self.l2mgmt = "1.3.6.1.4.1.171.11.63.8.2"
        super(DES_3052, self).__init__(*args)


def get(str):
    return getattr(sys.modules[__name__], str, None)


