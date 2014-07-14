#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
app = Flask(__name__)
from lib import switch

@app.route("/", methods=['GET'])
def main():
    if request.method == "GET":
        ip = request.args.get('ip', '')
        port = request.args.get('port', '')
        data = request.args.get('data', '')
        if ip and port and data:
            try: int(port)
            except: return jsonify(status="ERROR", reason = "Port must be integer")
            if data not in ["all", "oper_state", "admin_state", "speed", "err_dis", "errors", "cable", "fdb", "binding", "blocked", "mcast_groups"]:
                return jsonify(status="ERROR", reason = "Data must be one of all, admin_state, oper_state, speed, err_dis, errors, cable, fdb, binding, blocked, mcast_groups")
            try: sw = switch.Switch(ip)
            except: return jsonify(status="ERROR", reason = "No SNMP Connection!")
            if data == 'all':
                return jsonify(status="OK",
                            descr = sw.action.portdescr(port),
                            oper_state = sw.action.operstatus(port),
                            admin_state = sw.action.adminstatus(port),
                            speed = sw.action.speed(port),
                            learning = sw.action.addrlearn(port),
                            err_dis = sw.action.err_disabled(port),
                            errors = sw.action.errors(port),
                            cable = sw.action.cablediag(port),
                            fdb = sw.action.portfdb(port),
                            binding = sw.action.addr_bind(port),
                            blocked = sw.action.addr_block(port),
                            mcast_profile = sw.action.mcast_profile(port),
                            mcast_groups = sw.action.mcast_groups(port)
                        )
            if data == 'admin_state':
                return jsonify(status="OK", oper_state = sw.action.admin_state(port))
            if data == 'oper_state':
                return jsonify(status="OK", oper_state = sw.action.operstatus(port))
            if data == 'speed':
                return jsonify(status="OK", speed = sw.action.speed(port))
            if data == 'err_dis':
                return jsonify(status="OK", err_dis = sw.action.err_disabled(port))
            if data == 'errors':
                return jsonify(status="OK", errors = sw.action.errors(port))
            if data == 'cable':
                return jsonify(status="OK", cable = sw.action.cablediag(port))
            if data == 'fdb':
                return jsonify(status="OK", fdb = sw.action.portfdb(port))
            if data == 'binding':
                return jsonify(status="OK", binding = sw.action.addr_bind(port))
            if data == 'blocked':
                return jsonify(status="OK", blocked = sw.action.addr_block(port))
            if data == 'mcast_groups':
                return jsonify(status="OK", mcast_groups = sw.action.mcast_groups(port))

        else:
            return jsonify(status="ERROR", reason="Not enough args")

if __name__ == "__main__":
    app.debug = True
    app.run(host="192.168.133.16")

