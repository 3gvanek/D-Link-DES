#!/usr/bin/env python

from lib import switch
import sys

sw = switch.Switch(sys.argv[1])
port = sys.argv[2]

print "%-20s %s" % ("Description:", sw.action.portdescr(port))
print "%-20s %s" % ("Oper status:", sw.action.operstatus(port))
print "%-20s %s" % ("Admin status:", sw.action.adminstatus(port))
print "%-20s %s" % ("Speed:", sw.action.speed(port))
print "%-20s %s" % ("Address learn:", sw.action.addrlearn(port))
print "%-20s %s" % ("Err disabled:", sw.action.err_disabled(port))
print "%-20s %s" % ("Errors:", sw.action.errors(port))
print "%-20s %s" % ("Cable diag:", sw.action.cablediag(port))
print "%-20s %s" % ("MAC Table:", sw.action.portfdb(port))
print "%-20s %s" % ("Binding:", sw.action.addr_bind(port))
print "%-20s %s" % ("Blocked:", sw.action.addr_block(port))
print "%-20s %s" % ("Profile:", sw.action.mcast_profile(port))
print "%-20s %s" % ("Groups:", sw.action.mcast_groups(port))

