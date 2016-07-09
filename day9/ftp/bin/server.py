#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,sys,socketserver
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import modules



if __name__ == '__main__':
    ip_port = tuple((modules.GetConfig('server','ip'),int(modules.GetConfig('server','port'))))
    print('FTP server is running...')
    server = socketserver.ThreadingTCPServer(ip_port,modules.MyFtpServer)
    server.serve_forever()
