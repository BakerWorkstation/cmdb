#!/usr/bin/env python

import time
import sqlite3

def insert(data):
    conn = sqlite3.connect('./test.db')
    address = data['ban_ip']
    ban_time = data['ban_time']
    timestamp = int(time.time())
    reason = data['reason']
  
    cu = conn.cursor()
    row = cu.execute('select ban_ip, ban_time from ip_time;')
    flag = 1
    for i in row:
        #print 'i :',i[0]
        #print 'address :',address
        if  address == i[0]:
            conn.execute("update ip_time set ban_time='%s', timestamp='%s' , remark='%s'  where ban_ip='%s';" % (ban_time, int(time.time()), reason, address))
            flag = 0
            break
    
    if flag == 1:
        conn.execute("insert into  ip_time (ban_ip, ban_time, timestamp, remark)  VALUES ('%s', '%s', '%s', '%s');" % (address, ban_time, timestamp, reason))
    conn.commit()
    conn.close()

def search(data):
    conn = sqlite3.connect('./test.db')
    cu = conn.cursor()
    row = cu.execute("select ban_time, ban_ip, timestamp, remark from ip_time where ban_ip like '%%%s%%';" % data)
    flag = 0
    list_info = []
    for line in row:
        timestamp = line[2]
        format = '%Y-%m-%d %H:%M:%S'
        value = time.localtime(int(timestamp))
        timestamp = time.strftime(format, value)
        list_info.append((timestamp, line[1], line[0], line[3]))
        flag = 1
    cu.close()
    conn.commit()
    conn.close()
    return list_info

def delete(data):
    conn = sqlite3.connect('./test.db')
    conn.execute("delete from ip_time where ban_ip='%s';" %  data)
    conn.commit()
    conn.close()

def traversal():
    conn = sqlite3.connect('./test.db')
    cu = conn.cursor()
    list_info = []
    row = cu.execute("select timestamp, ban_ip, ban_time from ip_time ;")
    for line in row:
        timestamp = line[0]
        format = '%Y-%m-%d %H:%M:%S'
        value = time.localtime(int(timestamp))
        timestamp = time.strftime(format, value)
        list_info.append(( line[1], line[2], timestamp))
    return list_info
