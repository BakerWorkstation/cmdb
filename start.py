#!/usr/bin/env python

import os
import sys
import time
import subprocess
from sync_db import sync_iptables


def  start_iptables():
    os.chdir('/opt/ban/')
    command1 = '/etc/init.d/iptables status'
    info1 =  os.popen(command1).read()
    if 'not running' in info1:
        os.system('/etc/init.d/iptables start &> /dev/null')
        for a in range(1,26):
            print '\rFirewall       Start [','#' * a, ' ' * (25-a) ,'] ',
            sys.stdout.flush()
            time.sleep(0.05)
        print '\rFirewall       Start',' ' * 37,'[\033[32m  OK  \033[0m]'
        sys.stdout.flush()
    else:
        print '\033[31m Firewall PID exist !\033[0m'
    

def sync_DB():
    for a in range(1,26):
        print '\rSync   DB  Iptables  [','#' * a, ' ' * (25-a) ,'] ',
        sys.stdout.flush()
        time.sleep(0.05)
    print '\rSync   DB   Iptables',' ' * 37,'[\033[32m  OK  \033[0m]'
    sys.stdout.flush()
    
def start_Daemon():
    command2 = 'ps -ef | grep -v grep | grep "Daemon.py"'
    info2 = os.popen(command2).read()
    if 'Daemon' in info2:
        print '\033[31m Daemon.py PID exist !\033[0m'
    else:
        subprocess.Popen('python ./Daemon.py', shell =  True)
        for a in range(1,26):
            print '\rDaemon         start [','#' * a, ' ' * (25-a) ,'] ',
            sys.stdout.flush()
            time.sleep(0.05)
        command3 = 'ps -ef | grep -v grep | grep "Daemon.py"'
        info3 = os.popen(command3).read()
        if 'Daemon' in info3:
            print '\rDaemon         start',' ' * 37,'[\033[32m  OK  \033[0m]'
        else:
            print '\rDaemon         start',' ' * 37,'[\033[31m Fail \033[0m]'
        sys.stdout.flush()
    
        for b in range(1,26):
            print '\rhandle_log     start [','#' * b, ' ' * (25-b) ,'] ',
            sys.stdout.flush()
            time.sleep(0.05)
        command4 = 'ps -ef | grep -v grep | grep "handle_log.py"'
        info4 = os.popen(command4).read()
        if 'handle_log' in info4:
            print '\rhandle_log     start',' ' * 37,'[\033[32m  OK  \033[0m]'
        else:
            print '\rhandle_log     start',' ' * 37,'[\033[31m Fail \033[0m]'
        sys.stdout.flush()
    
        for c in range(1,26):
            print '\rhandle_ip      start [','#' * c, ' ' * (25-c) ,'] ',
            sys.stdout.flush()
            time.sleep(0.05)
        command5 = 'ps -ef | grep -v grep | grep "handle_ip.py"'
        info5 = os.popen(command5).read()
        if 'handle_ip' in info5:
            print '\rhandle_ip      start',' ' * 37,'[\033[32m  OK  \033[0m]'
        else:
            print '\rhandle_ip      start',' ' * 37,'[\033[31m Fail \033[0m]'
        sys.stdout.flush()
    
        for d in range(1,26):
            print '\rweb_service    start [','#' * d, ' ' * (25-d) ,'] ',
            sys.stdout.flush()
            time.sleep(0.05)
        command6 = 'ps -ef | grep -v grep | grep "web_service.py"'
        info6 = os.popen(command6).read()
        if 'web_service' in info6:
            print '\rweb_service    start',' ' * 37,'[\033[32m  OK  \033[0m]'
        else:
            print '\rweb_service    start',' ' * 37,'[\033[31m Fail \033[0m]'
        sys.stdout.flush()
    
        for e in range(1,26):
            print '\rsocket_server  start [','#' * e, ' ' * (25-e) ,'] ',
            sys.stdout.flush()
            time.sleep(0.05)
        command7 = 'ps -ef | grep -v grep | grep "socket_server.py"'
        info7 = os.popen(command7).read()
        if 'socket_server' in info7:
            print '\rsocket_server  start',' ' * 37,'[\033[32m  OK  \033[0m]'
        else:
            print '\rsocket_server  start',' ' * 37,'[\033[31m Fail \033[0m]'
        sys.stdout.flush()

if  __name__ == '__main__':
    start_iptables()
    sync_iptables() 
    sync_DB()
    start_Daemon()
