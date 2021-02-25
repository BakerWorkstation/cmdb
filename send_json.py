#!/usr/bin/env python

import json
import urllib2

def send_data(values, ip = '127.0.0.1', port = '8888'):
    url = 'http://%s:%s' % (ip, port)
    jdata = json.dumps(values)

    req = urllib2.Request(url)
    req.add_data(jdata)
    response = urllib2.urlopen(req,timeout = 5)
