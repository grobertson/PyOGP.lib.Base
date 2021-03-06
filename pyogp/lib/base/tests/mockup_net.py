
"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/trunk/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/lib/base/LICENSE.txt

$/LicenseInfo$
"""

import socket
import random

from pyogp.lib.base.message.circuit import Host

class MockupUDPServer(object):
    def __init__(self):
        self.rec_buffer = ''
        self.ip = 'MockupUDPServer'
        self.port = 80
    def receive_message(self, client, receive_buffer):
        #print 'SERVER receive'
        self.rec_buffer = receive_buffer

    def send_message(self, client, send_message):
        #print 'SERVER send'
        client.rec = send_message
        client.sender = Host((self, self.port))

#returns true if packet was sent successfully
class MockupUDPClient(object):

    def __init__(self):
        self.rec = ''
        self.sender = None
        self.socket = None

    def get_sender(self):
        return self.sender

    def set_response(self, response):
        self.rec[self.socket] = response

    def send_packet(self, send_buffer, host):
        #host is a mockup server
        #print 'CLIENT send'
        host.ip.receive_message(self, send_buffer)
        return True

    def receive_packet(self):
        #print 'CLIENT receive'
        data = self.rec
        self.rec = ''

        if len(data) > 0:
            return data, len(data)

        return '', 0

    def start_udp_connection(self):
        """ Starts a udp connection, returning socket and port. """
        self.socket = random.randint(0,80)
        return self.socket



