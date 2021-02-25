#!/usr/bin/env python

import sqlite3
import datetime

def  inittab():
    conn = sqlite3.connect('./test.db')
    conn.execute('''create table ip_time(id INTEGER Primary key AutoIncrement,ban_ip char(100) ,ban_time char(10),timestamp char(30), remark char(1000));''')
    conn.commit()
    conn.close()

def insert():
    conn = sqlite3.connect('./test.db')
    conn.execute("insert into  ip_time (ban_ip, ban_time, timestamp, remark)  VALUES ('127.0.0.1', '20h', '%s', 'have problem');" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    conn.execute("insert into  ip_time (ban_ip, ban_time, timestamp, remark)  VALUES ('192.0.0.1', '20h', '%s', 'have problem');" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    inittab()
    #insert()
