#!/usr/bin/env python

import subprocess
from time import time

 
popen = subprocess.Popen( 
                          'tail -0f /var/log/secure',
                          stdout = subprocess.PIPE,
                          stderr = subprocess.PIPE,
                          shell = True 
                         )

error_list = [
              'authentication failure',
              
              'Authentication failure',
              
              'authentication error',
              
              'Authentication error',

              'not known to the underlying authentication module for',
              
              'LOGIN REFUSED',
 
              'not allowed because not listed in AllowUsers',
     
              'not allowed because not in any group',
 
              'refused connect from',

              'Auth fail',
 
              'not allowed because a group is listed in DenyGroups',

              'not allowed because none of user\'s groups are listed in AllowGroups',
  
              'Failed password for',
             ]
while True:
    line = popen.stdout.readline().strip()
    print line
    for i in error_list:
        if i in line:
            try:
                print 'i : %s\n\n' % line.split('rhost=')[1].split(' ')[0]
                host   =  line.split('rhost=')[1].split(' ')[0]
            except:
                try:
                    print 'i : %s\n\n' % line.split('from')[1].split(' ')[1]
                    host =  line.split('from')[1].split(' ')[1]
                except:
                    host = ''
            if host:
                time_stamp = int(time())
                logfile = '%s.log' % i
                ff = open('./error_log/%s' % logfile, 'ab')
                ff.write(host + '\t' + str(time_stamp) + '\n')
                ff.close()
