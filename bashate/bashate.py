#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import

import argparse
import fileinput
import re
import sys

from bashate import messages

MESSAGES = messages.MESSAGES


def not_continuation(line):
    return not re.search('\\\\$', line)


def check_for_do(line, report):
    if not_continuation(line):
        match = re.match('^\s*(for|while|until)\s', line)
        if match:
            operator = match.group(1).strip()
            if operator == "for":
                # "for i in ..." and "for ((" is bash, but
                # "for (" is likely from an embedded awk script,
                # so skip it
                if re.search('for \([^\(]', line):
                    return
            if not re.search(';\s*do$', line):
                report.print_error((MESSAGES['E010'].msg % operator), line)


def check_if_then(line, report):
    if not_continuation(line):
        if re.search('^\s*(el)?if \[', line):
            if not re.search(';\s*then$', line):
                report.print_error(MESSAGES['E011'].msg, line)


def check_no_trailing_whitespace(line, report):
    if re.search('[ \t]+$', line):
        report.print_error(MESSAGES['E001'].msg, line)


def check_indents(line, report):
    m = re.search('^(?P<indent>[ \t]+)', line)
    if m:
        if re.search('\t', m.group('indent')):
            report.print_error(MESSAGES['E002'].msg, line)
        if (len(m.group('indent')) % 4) != 0:
            report.print_error(MESSAGES['E003'].msg, line)


def check_function_decl(line, report):
    failed = False
    if line.startswith("function"):
        if not re.search('^function [\w-]* \{$', line):
            failed = True
    else:
        # catch the case without "function", e.g.
        # things like '^foo() {'
        if re.search('^\s*?\(\)\s*?\{', line):
            failed = True

    if failed:
        report.print_error(MESSAGES['E020'].msg, line)


def starts_multiline(line):
    m = re.search("[^<]<<\s*(?P<token>\w+)", line)
    return m.group('token') if m else False


def end_of_multiline(line, token):
    return token and re.search("^%s\s*$" % token, line)


def check_arithmetic(line, report):
    if "$[" in line:
        report.print_error(MESSAGES['E041'].msg, line)


def check_hashbang(line, filename, report):
    # this check only runs on the first line
    #  maybe this should check for shell?
    if not line.startswith("#!") and not filename.endswith(".sh"):
        report.print_error(MESSAGES['E005'].msg, line)


class BashateRun(object):

    def __init__(self):
        # TODO(mrodden): rename these to match convention
        self.ERRORS = 0
        self.ERRORS_LIST = None
        self.IGNORE_LIST = None
        self.WARNINGS = 0
        self.WARNINGS_LIST = None

    def register_ignores(self, ignores):
        if ignores:
            self.IGNORE_LIST = '^(' + '|'.join(ignores.split(',')) + ')'

    def register_warnings(self, warnings):
        if warnings:
            self.WARNINGS_LIST = '^(' + '|'.join(warnings.split(',')) + ')'

    def register_errors(self, errors):
        if errors:
            self.ERRORS_LIST = '^(' + '|'.join(errors.split(',')) + ')'

    def should_ignore(self, error):
        return self.IGNORE_LIST and re.search(self.IGNORE_LIST, error)

    def should_warn(self, error):
        # if in the errors list, overrides warning level
        if self.ERRORS_LIST and re.search(self.ERRORS_LIST, error):
            return False
        if messages.is_default_warning(error):
            return True
        return self.WARNINGS_LIST and re.search(self.WARNINGS_LIST, error)

    def print_error(self, error, line,
                    filename=None, filelineno=None):
        if self.should_ignore(error):
            return

        warn = self.should_warn(error)

        if not filename:
            filename = fileinput.filename()
        if not filelineno:
            filelineno = fileinput.filelineno()
        if warn:
            self.WARNINGS = self.WARNINGS + 1
        else:
            self.ERRORS = self.ERRORS + 1

        self.log_error(error, line, filename, filelineno, warn)

    def log_error(self, error, line, filename, filelineno, warn=False):
        print("[%(warn)s] %(error)s: '%(line)s'" %
              {'warn': "W" if warn else "E",
               'error': error,
               'line': line.rstrip('\n')})
        print(" - %s : L%s" % (filename, filelineno))

    def check_files(self, files, verbose):
        in_multiline = False
        multiline_start = 0
        multiline_line = ""
        logical_line = ""
        token = False
        prev_file = None
        prev_line = ""
        prev_lineno = 0

        # NOTE(mrodden): magic; replace with proper
        # report class when necessary
        report = self

        for fname in files:
            for line in fileinput.input(fname):
                if fileinput.isfirstline():
                    # if in_multiline when the new file starts then we didn't
                    # find the end of a heredoc in the last file.
                    if in_multiline:
                        report.print_error(
                            MESSAGES['E012'].msg,
                            multiline_line,
                            filename=prev_file,
                            filelineno=multiline_start)
                        in_multiline = False

                    # last line of a previous file should always end with a
                    # newline
                    if prev_file and not prev_line.endswith('\n'):
                        report.print_error(
                            MESSAGES['E004'].msg,
                            prev_line,
                            filename=prev_file,
                            filelineno=prev_lineno)

                    prev_file = fileinput.filename()

                    check_hashbang(line, fileinput.filename(), report)

                    if verbose:
                        print("Running bashate on %s" % fileinput.filename())

                # NOTE(sdague): multiline processing of heredocs is interesting
                if not in_multiline:
                    logical_line = line
                    token = starts_multiline(line)
                    if token:
                        in_multiline = True
                        multiline_start = fileinput.filelineno()
                        multiline_line = line
                        continue
                else:
                    logical_line = logical_line + line
                    if not end_of_multiline(line, token):
                        continue
                    else:
                        in_multiline = False

                # Don't run any tests on comment lines
                if logical_line.lstrip().startswith('#'):
                    prev_line = logical_line
                    prev_lineno = fileinput.filelineno()
                    continue

                # Strip trailing comments. From bash:
                #
                #   a word beginning with # causes that word and all
                #   remaining characters on that line to be ignored.
                #   ...
                #   A character that, when unquoted, separates
                #   words. One of the following: | & ; ( ) < > space
                #   tab
                #
                # for simplicity, we strip inline comments by
                # matching just '<space>#'.
                ll_split = logical_line.split(' #', 1)
                if len(ll_split) > 1:
                    logical_line = ll_split[0].rstrip()

                check_no_trailing_whitespace(logical_line, report)
                check_indents(logical_line, report)
                check_for_do(logical_line, report)
                check_if_then(logical_line, report)
                check_function_decl(logical_line, report)
                check_arithmetic(logical_line, report)

                prev_line = logical_line
                prev_lineno = fileinput.filelineno()


def main():

    parser = argparse.ArgumentParser(
        description='A bash script style checker')
    parser.add_argument('files', metavar='file', nargs='*',
                        help='files to scan for errors')
    parser.add_argument('-i', '--ignore', help='Rules to ignore')
    parser.add_argument('-w', '--warn',
                        help='Rules to always warn (rather than error)')
    parser.add_argument('-e', '--error',
                        help='Rules to always error (rather than warn)')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-s', '--show', action='store_true', default=False)
    opts = parser.parse_args()

    if opts.show:
        messages.print_messages()
        sys.exit(0)

    files = opts.files
    if not files:
        parser.print_usage()
        return 1

    run = BashateRun()
    run.register_ignores(opts.ignore)
    run.register_warnings(opts.warn)
    run.register_errors(opts.error)

    try:
        run.check_files(files, opts.verbose)
    except IOError as e:
        print("bashate: %s" % e)
        return 1

    if run.WARNINGS > 0:
        print("%d bashate warning(s) found" % run.WARNINGS)

    if run.ERRORS > 0:
        print("%d bashate error(s) found" % run.ERRORS)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
