#!/usr/bin/env python

import sys
import time
import subprocess

def Main():

    flag1 = True
    flag2 = True
    flag3 = True
    flag4 = True

    while True:

        #if not flag4 == None:
        #    p4 = subprocess.Popen(
        #                          [ 'python', './socket_server.py' ],
        #                          stdout=subprocess.PIPE
        #                         )
        #flag4 = p4.poll()

       

        if not flag3 == None:
            p3 = subprocess.Popen(
                                  [ 'python', './web_server.py' ],
                                  stdout=subprocess.PIPE
                                 )
        flag3 = p3.poll()

    
        time.sleep(0.1)

        if not flag1 == None:
            p1 = subprocess.Popen(
                                  [ 'python', './sync_db.py' ],
                                  stdout=subprocess.PIPE
                                 )
        flag1 = p1.poll()
    
        time.sleep(0.1)

if __name__ == '__main__':
    Main()
