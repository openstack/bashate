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
test_bashate
----------------------------------

Tests for `bashate` module.
"""

import mock

from bashate import bashate
from bashate.tests import base


class TestBashate(base.TestCase):

    def setUp(self):
        super(TestBashate, self).setUp()
        self.run = bashate.BashateRun()

    def test_multi_ignore_with_slash(self):
        self.run.register_ignores('E001|E011')
        bashate.check_no_trailing_whitespace("if ", self.run)
        bashate.check_if_then("if ", self.run)

        self.assertEqual(0, self.run.ERRORS)

    def test_multi_ignore_with_comma(self):
        self.run.register_ignores('E001,E011')
        bashate.check_no_trailing_whitespace("if ", self.run)
        bashate.check_if_then("if ", self.run)

        self.assertEqual(0, self.run.ERRORS)

    def test_multi_ignore_mixed(self):
        self.run.register_ignores('E001|E002,E003|E011')
        bashate.check_no_trailing_whitespace("if ", self.run)
        bashate.check_if_then("if ", self.run)
        bashate.check_indents("  echo", self.run)

        self.assertEqual(0, self.run.ERRORS)

    def test_ignore(self):
        self.run.register_ignores('E001')
        bashate.check_no_trailing_whitespace("if ", self.run)

        self.assertEqual(0, self.run.ERRORS)

    @mock.patch('bashate.bashate.BashateRun.print_error')
    def test_while_check_for_do(self, m_print_error):
        test_line = 'while `do something args`'
        bashate.check_for_do(test_line, self.run)

        m_print_error.assert_called_once_with(
            'E010: Do not on same line as while', test_line)


class TestBashateSamples(base.TestCase):
    """End to end regression testing of bashate against script samples."""

    def setUp(self):
        super(TestBashateSamples, self).setUp()
        log_error_patcher = mock.patch(
            'bashate.bashate.BashateRun.log_error')
        self.m_log_error = log_error_patcher.start()
        self.run = bashate.BashateRun()
        self.addCleanup(log_error_patcher.stop)

    def assert_error_found(self, error, lineno):
        error_found = False
        for call in self.m_log_error.call_args_list:
            # unwrap args
            args = call[0]
            if (args[0].startswith(error) and lineno == args[3]):
                error_found = True
        if not error_found:
            self.fail('Error %s expected at line %d not found!' %
                      (error, lineno))

    def test_sample_E001(self):
        test_files = ['bashate/tests/samples/E001_bad.sh']
        self.run.check_files(test_files, False)

        self.assert_error_found('E001', 4)

    def test_sample_E002(self):
        test_files = ['bashate/tests/samples/E002_bad.sh']
        self.run.check_files(test_files, False)

        self.assert_error_found('E002', 3)

    def test_sample_E011(self):
        test_files = ['bashate/tests/samples/E011_bad.sh']
        self.run.check_files(test_files, False)

        self.assert_error_found('E011', 3)
        self.assert_error_found('E011', 6)

    def test_sample_E041(self):
        test_files = ['bashate/tests/samples/E041_bad.sh']
        self.run.check_files(test_files, False)

        self.assert_error_found('E041', 4)

    def test_sample_for_loops(self):
        test_files = ['bashate/tests/samples/for_loops.sh']
        self.run.check_files(test_files, False)

        self.assert_error_found('E010', 14)
        self.assert_error_found('E010', 20)

    def test_sample_comments(self):
        test_files = ['bashate/tests/samples/comments.sh']
        self.run.check_files(test_files, False)

        self.assertEqual(0, self.run.ERRORS)

    def test_pre_zero_dot_one_sample_file(self):
        """Test the sample file with all pre 0.1.0 release checks.

        This is a legacy compatibility check to make sure we still
        catch the same errors as we did before the first 0.1.0
        release of the bashate pypi package. There were no tests
        before this, so it is our baseline regression check.

        New checks shouldn't need to be added here, and should
        have their own separate unit test and/or sample file checks.
        """

        test_files = ['bashate/tests/samples/legacy_sample.sh']
        self.run.check_files(test_files, False)

        # NOTE(mrodden): E012 actually requires iterating more than one
        # file to detect at the moment; this is bug
        expected_errors = [
            ('E002', 4),
            ('E003', 6),
            ('E001', 10),
            ('E010', 13),
            ('E010', 18),
            ('E010', 23),
            ('E011', 29),
            ('E020', 3)
        ]

        for error in expected_errors:
            self.assert_error_found(*error)
