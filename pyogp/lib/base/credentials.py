"""
@file credentials.py
@date 2008-09-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# standard python libs
import md5

# related
from indra.base import llsd

# pyogp
import exc

class PlainPasswordCredential(object):
    """a plain password credential"""
    

    PW_TYPE = "plain"
    
    def __init__(self, firstname, lastname, password):
        """initialize this credential"""
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
    
    def __repr__(self):
        """return a string representation"""
        return "PlainPasswordCredential for '%s %s'" %(self.firstname, self.lastname)
    
    def get_xmlrpc_login_params(self):
        """ return a dictionary of login params """
        
        login_params = {
            'first': self.firstname,
            'last': self.lastname,
            'passwd': self.password
        }
        
        return login_params

    def serialize(self):
        """return the credential as a string"""
        
        loginparams={
                'password'     : self.password,
                'lastname'     : self.lastname,
                'firstname'    : self.firstname
        }

        llsdlist = llsd.format_xml(loginparams)
        return llsdlist

    @property
    def content_type(self):
        """return HTTP headers needed here"""
        return "application/llsd+xml"

class MD5PasswordCredential(object):
    """a md5 password credential"""

    PW_TYPE = "md5"
    
    def __init__(self, firstname, lastname, plainpw='', md5pw=None):
        """initialize this credential"""
        self.firstname = firstname
        self.lastname = lastname
        if md5pw is not None:
            self.password = md5pw
        else:
            self.password = md5.new(plainpw).hexdigest()
    
    def __repr__(self):
        """return a string represenation"""
        return "MD5PasswordCredential for '%s %s'" %(self.firstname, self.lastname)



class LLSDSerializer(PlainPasswordCredential):
    """converts a plain password credential to LLSD
    
    Here is how you can use it:
    >>> credential = PlainPasswordCredential('Firstname','Lastname','password')
    >>> serializer = LLSDSerializer(credential)
    >>> serializer.serialize()
    '<?xml version="1.0" ?><llsd><map><key>lastname</key><string>Lastname</string><key>password</key><string>password</string><key>firstname</key><string>Firstname</string></map></llsd>'
    >>> serializer.content_type
    'application/llsd+xml'
    """

    def __init__(self, context):
        """initialize this adapter by storing the context (the credential)"""
        self.context = context

    def serialize(self):
        """return the credential as a string"""
        
        loginparams={
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

class MD5PasswordLLSDSerializer(MD5PasswordCredential):
    """converts a md5 credential object to LLSD XML
    """

    def __init__(self, context):
        """initialize this adapter by storing the context (the credential)"""
        self.context = context

    def serialize(self):
        """return the credential as a string"""
        
        loginparams={
                'md5-password' : self.context.password,
                'lastname'     : self.context.lastname,
                'firstname'    : self.context.firstname
        }

        llsdlist = llsd.format_xml(loginparams)
        return llsdlist

    @property
    def content_type(self):
        """return HTTP headers needed here"""
        return "application/llsd+xml"

class CredentialLLSDDeserializer(object):
    """take an LLSD string and create a credential object

    This is a utility
    """

    def deserialize(self, s):
        payload = llsd.parse(s)
        
        # now we dispatch which credential object we need to instantiate
        # this simply depends whether it's md5-password or password we find
        keys = payload.keys()
        if 'firstname' in keys and 'lastname' in keys:
            if payload.has_key("password"):
                return PlainPasswordCredential(payload['firstname'], payload['lastname'], payload['password'])
            elif payload.has_key("md5-password"):
                return MD5PasswordCredential(payload['firstname'], payload['lastname'], md5pw=payload['md5-password'])
        raise exc.CredentialDeserializerNotFound(str(payload))

