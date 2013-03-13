# vim: set fileencoding=utf-8 :

import ioc
import os
import unittest

current_dir = os.path.dirname(os.path.realpath(__file__))

class TestHelper(unittest.TestCase):

    def test_build(self):
        container = ioc.build([
            "%s/../fixtures/services.yml" % current_dir
        ])

        self.assertEquals(2, len(container.services))
        self.assertEquals(container.get('foo').fake, container.get('fake'))
        self.assertEquals('argument 1', container.get('fake').mandatory)