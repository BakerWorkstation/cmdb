#!/usr/bin/env python

from socket import *
import json


def send_data(data):
    HOST = '127.0.0.1'
    PORT = 50000
    BUFSIZ = 1024
    ADDR = (HOST, PORT)



    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)

    # testdict={"filename":"11","filedata":"asasss","index":"upload"}
    send = json.dumps(data)
    tcpCliSock.send(send)
    
    tcpCliSock.close()

