
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

# std python libs
import socket
from logging import getLogger

from pyogp.lib.base.message.circuit import Host

logger = getLogger('net.net')

#returns true if packet was sent successfully
class NetUDPClient(object):

    def __init__(self):

        self.sender = Host((None, None))
        self.socket = None

    def get_sender(self):

        return self.sender

    def send_packet(self, send_buffer, host):

        if send_buffer == None:
            raise Exception("No data specified")

        bytes = self.socket.sendto(send_buffer, (host.ip, host.port))

    def receive_packet(self):

        buf = 10000
        try:
            data, addr = self.socket.recvfrom(buf)
        except:
            return '', 0

        self.sender.ip = addr[0]
        self.sender.port = addr[1]

        return data, len(data)

    def start_udp_connection(self):
        """ Starts a udp connection, returning socket and port. """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        return self.socket

    def __repr__(self):

        return self.sender.__repr__
