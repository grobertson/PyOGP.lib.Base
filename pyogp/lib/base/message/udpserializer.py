
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

#standard libs
import struct
from logging import getLogger

# pygop
from msgtypes import MsgType, MsgBlockType, EndianType
from data_packer import DataPacker
from template_dict import TemplateDictionary
from pyogp.lib.base import exc
from pyogp.lib.base.message.message_dot_xml import MessageDotXML

logger = getLogger('message.udpserializer') 

class UDPMessageSerializer(object):
    """ an adpater for serializing a IUDPMessage into the UDP message format

        This class builds messages at its high level, that is, keeping
        that data in data structure form. A serializer should be used on
        the message produced by this so that it can be sent over a network. """

    def __init__(self, message_template = None, message_xml = None):
        """initialize the adapter"""
        self.context = None	# the UDPMessage

        self.template_dict = TemplateDictionary(message_template)
        self.current_template = None
        self.packer = DataPacker()

        if not message_xml:
            self.message_xml = MessageDotXML()
        else:
            self.message_xml = message_xml

    def set_current_template(self):
        """ establish the template for the current packet """

        self.current_template = self.template_dict.get_template(self.context.name)

    def serialize(self, context):
        """ Builds the message by serializing the data. Creates a packet ready
            to be sent. """

        self.context = context

        self.set_current_template()

        # validate whether we are allowed to receive this message over udp
        if not self.message_xml.validate_udp_msg(self.current_template.name):
            logger.warning("Sending '%s' over UDP, which is deprecated. Discarding." % (self.current_template.name))
            return None

        #doesn't build in the header flags, sequence number, or data offset
        msg_buffer = ''
        bytes = 0

        #put the flags in the begining of the data. NOTE: for 1 byte, endian doesn't matter
        msg_buffer += self.packer.pack_data(self.context.send_flags, MsgType.MVT_U8)

        #set packet ID
        msg_buffer += self.packer.pack_data(self.context.packet_id, \
                                                  MsgType.MVT_S32, \
                                                  endian_type=EndianType.BIG)

        #pack in the offset to the data. NOTE: for 1 byte, endian doesn't matter
        msg_buffer += self.packer.pack_data(0, MsgType.MVT_U8)

        if self.current_template == None:
            return None

        #don't need to pack the frequency and message number. The template
        #stores it because it doesn't change per template.
        pack_freq_num = self.current_template.msg_num_hex
        msg_buffer += pack_freq_num
        bytes += len(pack_freq_num)

        #message_data = self.context.message_data

        for block in self.current_template.get_blocks():
            packed_block, block_size = self.build_block(block, context)
            msg_buffer += packed_block
            bytes += block_size

        if self.current_template.name == 'RegionHandshakeReply':
            # testing a hack to let RegionHandshakeReply get parsed
            msg_buffer += struct.pack(">I", 0)

        self.message_buffer = msg_buffer

        return msg_buffer

    def build_block(self, template_block, message_data):
        block_buffer = ''
        bytes = 0

        #the MsgData blocks is a list of lists
        #each block in the list is a block_list because you can have more than
        #one block for any given name
        block_list = message_data.get_block(template_block.name)
        block_count = len(block_list)

        #multiple block type means there is a static number of these blocks
        #that make up this message, with the number stored in the template
        #don't need to add it to the buffer, because the message handlers that
        #receieve this know how many to read automatically
        if template_block.block_type == MsgBlockType.MBT_MULTIPLE:
            if template_block.number != block_count:
                raise exc.MessageSerializationError(template_block.name, "block data mismatch")

        #variable means the block variables can repeat, so we have to
        #mark how many blocks there are of this type that repeat, stored in
        #the data
        if template_block.block_type == MsgBlockType.MBT_VARIABLE:
            block_buffer += struct.pack('>B', block_count)
            bytes += 1            

        for block in block_list:

            for v in template_block.get_variables(): #message_block.get_variables():
                #this mapping has to occur to make sure the data is written in correct order
                variable = block.get_variable(v.name)
                var_size  = v.size
                var_data  = variable.data

                data = self.packer.pack_data(var_data, v.type)

                if variable == None:
                    raise exc.MessageSerializationError(variable.name, "variable value is not set")


                #if its a VARIABLE type, we have to write in the size of the data
                if v.type == MsgType.MVT_VARIABLE:
                    #data_size = template_block.get_variable(variable.name).size
                    if var_size == 1:
                        block_buffer += self.packer.pack_data(len(data), MsgType.MVT_U8)
                        #block_buffer += struct.pack('>B', var_size)
                    elif var_size == 2:
                        block_buffer += self.packer.pack_data(len(data), MsgType.MVT_U16)
                        #block_buffer += struct.pack('>H', var_size)
                    elif var_size == 4:
                        block_buffer += self.packer.pack_data(len(data), MsgType.MVT_U32)
                        #block_buffer += struct.pack('>I', var_size)
                    else:
                        raise exc.MessageSerializationError("variable size", "unrecognized variable size")

                    bytes += var_size

                block_buffer += data
                bytes += len(data)

        return block_buffer, bytes



