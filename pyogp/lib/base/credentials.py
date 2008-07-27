from zope.interface import implements
from zope.component import adapts

import md5

from indra.base import llsd

import grokcore.component as grok

from interfaces import IPlainPasswordCredential, ISerialization, ICredentialDeserialization

class PlainPasswordCredential(object):
    """a plain password credential"""
    
    implements(IPlainPasswordCredential)
    
    def __init__(self, firstname, lastname, password):
        """initialize this credential"""
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        

# an adapter to serialize this to LLSD

class PlainPasswordLLSDSerializer(grok.Adapter):
    """converts a plain password credential to LLSD
    
    Here is how you can use it:
    >>> credential = PlainPasswordCredential('Firstname','Lastname','password')
    >>> serializer = ISerialization(credential)
    >>> serializer.serialize()
    '<?xml version="1.0" ?><llsd><map><key>lastname</key><string>Lastname</string><key>password</key><string>password</string><key>firstname</key><string>Firstname</string></map></llsd>'
    >>> serializer.content_type
    'application/llsd+xml'
    """
    
    grok.implements(ISerialization)
    grok.context(IPlainPasswordCredential)
    
    def __init__(self, context):
        """initialize this adapter by storing the context (the credential)"""
        self.context = context

    def serialize(self):
        """return the credential as a string"""
        
        loginparams={
#                'password'      : "$1$"+md5.new(self.context.password).hexdigest(),
                'password'      : self.context.password,
                'lastname'     : self.context.lastname,
                'firstname'    : self.context.firstname
        }

        llsdlist = llsd.format_xml(loginparams)
        return llsdlist

    @property
    def content_type(self):
        """return HTTP headers needed here"""
        return "application/llsd+xml"


class PlainPasswordLLSDDeserializer(grok.GlobalUtility):
    """take an LLSD string and create a credential object

    This is a utility
    """
    grok.implements(ICredentialDeserialization)
    grok.name('application/llsd+xml')

    def deserialize(self, s):
        payload = llsd.parse(s)
        # TODO: make this serialization stuff more flexible in terms of other types
        return PlainPasswordCredential(payload['firstname'], payload['lastname'], payload['password'])