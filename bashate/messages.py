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

import re
import textwrap


class _Message(object):
    """An individual bashate message.

    This should be accessed via the MESSAGES dict keyed by msg_id,
    e.g.

      from bashate.messages import MESSAGES
      print(MESSAGES['E123'].msg)

    :param msg_id: The unique message id (E...)
    :param msg_str: The short message string, as displayed in program
                     output
    :param long_msg: A longer more involved message, designed for
                     documentation
    """
    def __init__(self, msg_id, msg_str, long_msg, default):
        self.msg_id = msg_id
        self.msg_str = msg_str
        # clean-up from """ to a plain string
        if long_msg:
            self.long_msg = textwrap.dedent(long_msg)
            self.long_msg = self.long_msg.strip()
        else:
            self.long_msg = None
        self.default = default

    @property
    def msg(self):
        # For historical reasons, the code relies on "id: msg" so build
        # that up as .msg property for quick access.
        return "%s: %s" % (self.msg_id, self.msg_str)


_messages = {
    'E001': {
        'msg': 'Trailing Whitespace',
        'long_msg': None,
        'default': 'E'
    },
    'E002': {
        'msg': 'Tab indents',
        'long_msg':
        """
        Spaces are preferred to tabs in source files.
        """,
        'default': 'E'
    },
    'E003': {
        'msg': 'Indent not multiple of 4',
        'long_msg':
        """
        Four spaces should be used to offset logical blocks.
        """,
        'default': 'E'
    },
    'E004': {
        'msg': 'File did not end with a newline',
        'long_msg':
        """
        It is conventional to have a single newline ending files.
        """,
        'default': 'E'
    },
    'E005': {
        'msg': 'File does not begin with #! or have .sh prefix',
        'long_msg':
        """
        This can be useful for tools that use either the interpreter
        directive or the file-exension to select highlighting mode,
        syntax mode or determine MIME-type, such as file, gerrit and
        editors.
        """,
        'default': 'W'
    },
    'E006': {
        'msg': 'Line too long',
        'long_msg':
        """
        This check mimics the widely accepted convention from PEP8 and
        many other places that lines longer than a standard terminal width
        (default=79 columns) can not only cause problems when reading/writing
        code, but also often indicates a bad smell, e.g. too many levels
        of indentation due to overly complex functions which require
        refactoring into smaller chunks.
        """,
        'default': 'W'
    },
    'E010': {
        'msg': 'The "do" should be on same line as %s',
        'long_msg':
        """
        Ensure consistency of "do" directive being on the same line as
        it's command.  For example:

           for i in $(seq 1 100);
           do
              echo "hi"
           done

        will trigger this error
        """,
        'default': 'E'
    },
    'E011': {
        'msg': 'Then keyword is not on same line as if or elif keyword',
        'long_msg':
        """
        Similar to E010, this ensures consistency of if/elif statements
        """,
        'default': 'E'
    },
    'E012': {
        'msg': 'here-document at line %d delimited by end-of-file',
        'long_msg':
        """
        This check ensures the closure of heredocs (<<EOF directives).
        Bash will warn when a heredoc is delimited by end-of-file, but
        it is easily missed and can cause unexpected issues when a
        file is sourced.
        """,
        'default': 'E'
    },
    'E020': {
        'msg': 'Function declaration not in format ^function name {$',
        'long_msg':
        """
        There are several equivalent ways to define functions in Bash.
        This check is for consistency.
        """,
        'default': 'E'
    },
    'E040': {
        'msg': 'Syntax error',
        'long_msg':
        """
        `bash -n` determined that there was a syntax error preventing
        the script from parsing correctly and running.
        """,
        'default': 'E'
    },
    'E041': {
        'msg': 'Arithmetic expansion using $[ is deprecated for $((',
        'long_msg':
        """
        $[ is deprecated and not explained in the Bash manual.  $((
        should be used for arithmetic.
        """,
        'default': 'E'
    },
    'E042': {
        'msg': 'local declaration hides errors',
        'long_msg':
        """
        The return value of "local" is always 0; errors in subshells
        used for declaration are thus hidden and will not trigger "set -e".
        """,
        'default': 'W',
    },
    'E043': {
        'msg': 'Arithmetic compound has inconsistent return semantics',
        'long_msg':
        """
        The return value of ((expr)) is 1 if "expr" evalues to zero,
        otherwise 0.  Combined with "set -e", this can be quite
        confusing when something like ((counter++)) evaluates to zero,
        making the arithmetic evaluation return 1 and triggering the
        an error failure.  It is therefore best to use assignment with
        the $(( operator.
        """,
        'default': 'W',
    },
    'E044': {
        'msg': 'Use [[ for non-POSIX comparisions',
        'long_msg':
        """
        [ is the POSIX test operator, while [[ is the bash keyword
        comparision operator.  Comparisons such as =~, < and > require
        the use of [[.
        """,
        'default': 'E',
    },
}

MESSAGES = {}

_default_errors = []
_default_warnings = []

for k, v in _messages.items():
    MESSAGES[k] = _Message(k, v['msg'], v['long_msg'], v['default'])

    if v['default'] == 'E':
        _default_errors.append(k)
    if v['default'] == 'W':
        _default_warnings.append(k)

# convert this to the regex strings.  This looks a bit weird
# but it fits the current model of error/warning/ignore checking
# easily.
_default_errors = '^(' + '|'.join(_default_errors) + ')'
_default_warnings = '^(' + '|'.join(_default_warnings) + ')'


def is_default_error(error):
    return re.search(_default_errors, error)


def is_default_warning(error):
    return re.search(_default_warnings, error)


def print_messages():

    print("\nAvailable bashate checks")
    print("------------------------\n")
    for k, v in MESSAGES.items():
        print(" [%(default)s] %(id)s : %(string)s" % {
            'default': v.default,
            'id': v.msg_id,
            'string': v.msg_str})
        if v.long_msg:
            for l in v.long_msg.split('\n'):
                print("            %s" % l)
        print("")
