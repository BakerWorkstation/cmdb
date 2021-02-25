# -*- encoding: utf-8 -*- 
#!/usr/bin/env python
 
import socket 
import select 
import json
import threading
import mod_config
import sqlite3
import time
from iptables import operate_iptables


class timer(threading.Thread):
    def __init__(self, info):
        threading.Thread.__init__(self)
        self.data = info
    def run(self):
        data = json.loads(self.data)
        #print data
        conn = sqlite3.connect('./test.db')
        cu = conn.cursor() 
        row = cu.execute("select ban_time from ip_time where ban_ip='%s';" % data['hostname'])
        flag = 0
        try:
            for i in row:
                conn.execute("update ip_time set ban_time='%s', timestamp='%s' where ban_ip='%s';" % (data['bantime'], int(time.time()), data['hostname']))
                #print 'update', i[0]
                flag = 1
                break
            if flag == 0:
                timestamp = int(time.time())
                reason = ''
                conn.execute("insert into  ip_time (ban_ip, ban_time, timestamp, remark)  VALUES ('%s', '%s', '%s', '%s');" % (data['hostname'], data['bantime'], timestamp, reason))

                operate_iptables('add', data['hostname'])
        except Exception as e:
            print e
            pass
        cu.close()
        conn.commit()
        conn.close()

def  main_loop():
    host = ""
    port = 50000  
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
    s.bind((host,port))  
    s.listen(5) 
    s.setblocking(0)
    while 1:  
        infds,outfds,errfds = select.select([s,],[],[],5)  
        sum = ''
        if len(infds) != 0:  
            clientsock,clientaddr = s.accept() 
            infds_c,outfds_c,errfds_c = select.select([clientsock,],[],[],3) 
            while len(infds_c) != 0:  
                buf = clientsock.recv(8192)  
                #infds_d,outfds_d,errfds_d = select.select([,],[],[],3) 
                if len(buf) != 0:  
                    sum += buf
                else:
                    t = timer(sum)
                    t.setDaemon(True)
                    t.start()
                    break

if  __name__ == '__main__':
    main_loop()
