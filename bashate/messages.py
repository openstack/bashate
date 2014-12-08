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


class _Message:
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
    def __init__(self, msg_id, msg_str, long_msg):
        self.msg_id = msg_id
        self.msg_str = msg_str
        self.long_msg = long_msg

    @property
    def msg(self):
        # For historical reasons, the code relies on "id: msg" so build
        # that up as .msg property for quick access.
        return "%s: %s" % (self.msg_id, self.msg_str)

_messages = {
    'E001': {
        'msg': 'Trailing Whitespace',
        'long_msg': None
    },
    'E002': {
        'msg': 'Tab indents',
        'long_msg': None
    },
    'E003': {
        'msg': 'Indent not multiple of 4',
        'long_msg': None
    },
    'E004': {
        'msg': 'File did not end with a newline',
        'long_msg': None
    },
    'E010': {
        'msg': 'Do not on same line as %s',
        'long_msg': None
    },
    'E011': {
        'msg': 'Then keyword is not on same line as if or elif keyword',
        'long_msg': None
    },
    'E012': {
        'msg': 'heredoc did not end before EOF',
        'long_msg': None
    },
    'E020': {
        'msg': 'Function declaration not in format ^function name {$',
        'long_msg': None
    },
    'E041': {
        'msg': 'Arithmetic expansion using $[ is deprecated for $((',
        'long_msg': None
    },
}

MESSAGES = {}
for k, v in _messages.items():
    MESSAGES[k] = _Message(k, v['msg'], v['long_msg'])


def print_messages():
    print("\nAvailable bashate checks")
    print("------------------------")
    for k, v in MESSAGES.items():
        print(" %(id)s : %(string)s" % {
            'id': v.msg_id,
            'string': v.msg_str})
    print("")
