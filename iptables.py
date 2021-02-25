#!/usr/bin/env python
import os

def operate_iptables(method, ip):
    if method == 'add':
        command1 = '''iptables -L INPUT | grep -v grep | grep '%s' ''' %  ip
        if not ip in os.popen(command1).read():
            command2 = '''iptables -I INPUT -s '%s' -j DROP''' % ip
            os.system(command2)

    if method == 'delete':
        command3 = '''iptables -L INPUT | grep -v grep | grep '%s' ''' %  ip
        if ip in os.popen(command3).read():
            command4 = "iptables -D INPUT `iptables  -L INPUT --line-number | grep '%s'|awk '{print $1}'`" % ip
            os.system(command4)
