#!/usr/bin/env python
#! -*- coding:UTF-8 -*-

import os
import re
import time
import sqlite3
import threading
from iptables import operate_iptables


def clear_iptables():
    os.system("iptables -F INPUT")
def sync_iptables():
    try:
        conn = sqlite3.connect('./test.db')
        cu = conn.cursor()
        row = cu.execute('select ban_ip from ip_time;')
        for i in row:
            command = 'iptables -L INPUT | grep -v grep | grep "%s"' % i[0]
            if i[0] in os.popen(command).read():
                continue
            else:
                operate_iptables('add', i[0])
    except:
        ff = open('./error_log/syncdb_error.log', 'ab')
        ff.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\t' + str(e) + '\n')
        ff.close()

# 查看bantime是否到达
class check_time(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        # 查看untiltime，时间快到的，需要从iptables删除相应行,数据库也要删除相应记录
        while True:
            try:
                conn = sqlite3.connect('./test.db')
                cu = conn.cursor()
                row = cu.execute('select ban_ip, ban_time, timestamp from ip_time;')
                for i in row:
                    ban_ip = i[0]
                    ban_time = i[1]
                    timestamp = i[2]

                    if re.match(r'^\d+$', ban_time):
                        if  int(time.time()) >  int(ban_time[0]) + int(timestamp):
                            operate_iptables('delete', ban_ip)
                            conn.execute('''delete from ip_time where ban_ip='%s';''' % ban_ip)

                    if re.match(r'^\d+[s|S]$', ban_time):
                        ban_time  =  re.split(r'[s|S]', ban_time)[0]
                        if  int(time.time()) >  int(ban_time) + int(timestamp):
                            operate_iptables('delete', ban_ip)
                            conn.execute('''delete from ip_time where ban_ip='%s';''' % ban_ip)


                    if re.match(r'^\d+[m|M]$', ban_time):
                        ban_time  =  re.split(r'[m|M]', ban_time)[0]
                        if  int(time.time()) >  int(ban_time) * 60 + int(timestamp):
                            operate_iptables('delete', ban_ip)
                            conn.execute('''delete from ip_time where ban_ip='%s';''' % ban_ip)

                    if re.match(r'^\d+[h|H]$', ban_time):
                        ban_time  =  re.split(r'[h|H]', ban_time)[0]
                        if  int(time.time()) >  int(ban_time) * 3600 + int(timestamp):
                            operate_iptables('delete', ban_ip)
                            conn.execute('''delete from ip_time where ban_ip='%s';''' % ban_ip)

                    if re.match(r'^\d+[d|D]$', ban_time):
                        ban_time  =  re.split(r'[d|D]', ban_time)[0]
                        if  int(time.time()) >  int(ban_time) * 86400 + int(timestamp):
                            operate_iptables('delete', ban_ip)
                            conn.execute('''delete from ip_time where ban_ip='%s';''' % ban_ip)
                cu.close()
                conn.commit()
                conn.close()
            except Exception as e:
                ff = open('./error_log/polling_DB_error.log', 'ab')
                ff.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\t' + str(e) + '\n')
                ff.close()
            time.sleep(0.5)



if __name__ == '__main__': 
    clear_iptables()
    sync_iptables()
    t = check_time()
    t.setDaemon(True)
    t.start()
    while True:
        pass
