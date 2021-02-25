#!/usr/bin/env python

import os
import re
import datetime
from socket_client import send_data


def loop_count():
    #while True:
        for filename in os.listdir('./source_log'):
            #filename = filename.replace(' ','\ ')
            
            ff =  open('./source_log/' + filename, 'r')
            for line in ff.readlines():
                line = line.strip()
                data = re.split(r'\s+', line)
          
                print '-' * 50
                print 'Time      : %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print 'IP        : \033[31m%s\033[0m' %  data[0]
                print 'bantime   : \033[31m%s \033[0m\n' % data[1]
                values = {'hostname' : data[0], 'bantime' : data[1]}
                send_data(values)

if __name__ == '__main__':
    loop_count()
