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

import argparse
import fileinput
import re
import sys


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
            if not re.search(';\s*do(\b|$)', line):
                report.print_error(('E010: Do not on same line as %s' %
                                    operator), line)


def check_if_then(line, report):
    if not_continuation(line):
        if re.search('^\s*(el)?if \[', line):
            if not re.search(';\s*then(\b|$)', line):
                report.print_error('E011: Then keyword is not on same line '
                                   'as if or elif keyword', line)


def check_no_trailing_whitespace(line, report):
    if re.search('[ \t]+$', line):
        report.print_error('E001: Trailing Whitespace', line)


def check_indents(line, report):
    m = re.search('^(?P<indent>[ \t]+)', line)
    if m:
        if re.search('\t', m.group('indent')):
            report.print_error('E002: Tab indents', line)
        if (len(m.group('indent')) % 4) != 0:
            report.print_error('E003: Indent not multiple of 4', line)


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
        report.print_error('E020: Function declaration not in format '
                           '"^function name {$"', line)


def starts_multiline(line):
    m = re.search("[^<]<<\s*(?P<token>\w+)", line)
    if m:
        return m.group('token')
    else:
        return False


def end_of_multiline(line, token):
    if token:
        return re.search("^%s\s*$" % token, line) is not None
    return False


def check_arithmetic(line, report):
    if "$[" in line:
        report.print_error('E041: Arithmetic expansion using $[ '
                           'is deprecated for $((', line)


class BashateRun(object):

    def __init__(self):
        # TODO(mrodden): rename these to match convention
        self.ERRORS = 0
        self.IGNORE = None

    def register_ignores(self, ignores):
        if ignores:
            self.IGNORE = '^(' + '|'.join(ignores.split(',')) + ')'

    def should_ignore(self, error):
        return self.IGNORE and re.search(self.IGNORE, error)

    def print_error(self, error, line,
                    filename=None, filelineno=None):
        if self.should_ignore(error):
            return
        if not filename:
            filename = fileinput.filename()
        if not filelineno:
            filelineno = fileinput.filelineno()
        self.ERRORS = self.ERRORS + 1
        self.log_error(error, line, filename, filelineno)

    def log_error(self, error, line, filename, filelineno):
        print("%s: '%s'" % (error, line.rstrip('\n')))
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
                            'E012: heredoc did not end before EOF',
                            multiline_line,
                            filename=prev_file,
                            filelineno=multiline_start)
                        in_multiline = False

                    # last line of a previous file should always end with a
                    # newline
                    if prev_file and not prev_line.endswith('\n'):
                        report.print_error(
                            'E004: file did not end with a newline',
                            prev_line,
                            filename=prev_file,
                            filelineno=prev_lineno)

                    prev_file = fileinput.filename()

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
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    opts = parser.parse_args()

    files = opts.files
    if not files:
        parser.print_usage()
        return 1

    run = BashateRun()
    run.register_ignores(opts.ignore)

    try:
        run.check_files(files, opts.verbose)
    except IOError as e:
        print("bashate: %s" % e)
        return 1

    if run.ERRORS > 0:
        print("%d bashate error(s) found" % run.ERRORS)
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
