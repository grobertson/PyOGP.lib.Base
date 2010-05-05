
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

# standard python modules
import unittest

# pyogp
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.exc import *
from pyogp.lib.base.tests.mockup_client import MockupClient
from pyogp.lib.base.tests.base import MockCapHandler

from logging import getLogger
# initialize logging
logger = getLogger('test_caps')

class TestCaps(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):

        self.restclient = MockupClient(MockCapHandler())

    def test_cap_constructor(self):

        from pyogp.lib.base.settings import Settings

        name = 'foo'
        url = 'http://127.0.0.1'
        settings = Settings()

        cap = Capability(name, 
                        url, 
                        restclient=self.restclient, 
                        settings=settings)

        self.assertEquals(name, cap.name)
        self.assertEquals(url, cap.public_url)
        self.assertEquals(self.restclient, cap.restclient)
        self.assertEquals(settings, cap.settings)

    def test_cap_GET(self):

        name = 'foo'
        url = 'http://127.0.0.1/good_cap'

        cap = Capability(name, url, restclient=self.restclient)
        response = cap.GET()

        self.assertEquals(response, {'foo':'bar'})

    def test_cap_GET_not_found(self):

        restclient = MockCapHandler()
        name = 'foo'
        url = 'http://127.0.0.1/bad_cap'

        cap = Capability(name, url, restclient=self.restclient)

        self.assertRaises(ResourceNotFound, cap.GET)

    def test_cap_GET_exception(self):

        restclient = MockCapHandler()
        name = 'foo'
        url = 'http://127.0.0.1/get_503'

        cap = Capability(name, url, restclient=self.restclient)

        self.assertRaises(ResourceError, cap.GET)        

    def test_cap_GET_no_deserializer(self):

        restclient = MockCapHandler()
        name = 'foo'
        url = 'http://127.0.0.1/get_no_llsd'

        cap = Capability(name, url, restclient=self.restclient)

        self.assertRaises(DeserializerNotFound, cap.GET)

    def test_cap_POST(self):

        name = 'foo'
        url = 'http://127.0.0.1/good_cap'
        data = {'foo':'bar'}

        cap = Capability(name, url, restclient=self.restclient)
        response = cap.POST(data)

        self.assertEquals(response, {'foo':'bar'})

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCaps))
    return suite



