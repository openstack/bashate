# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_bash8
----------------------------------

Tests for `bash8` module.
"""

from bash8 import bash8
from bash8.tests import base


class TestBash8(base.TestCase):

    def setUp(self):
        super(TestBash8, self).setUp()

        # cleanup global IGNOREs
        def reset_ignores():
            bash8.IGNORE = None
        self.addCleanup(reset_ignores)

    def test_multi_ignore(self):
        bash8.register_ignores('E001|E011')
        bash8.check_no_trailing_whitespace("if ")
        bash8.check_if_then("if ")
        self.assertEqual(bash8.ERRORS, 0)

    def test_ignore(self):
        bash8.register_ignores('E001')
        bash8.check_no_trailing_whitespace("if ")
        self.assertEqual(bash8.ERRORS, 0)
