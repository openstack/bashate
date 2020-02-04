===============================
bashate
===============================

A pep8 equivalent for bash scripts

This program attempts to be an automated style checker for bash scripts
to fill the same part of code review that pep8 does in most OpenStack
projects. It started from humble beginnings in the DevStack project,
and will continue to evolve over time.

The output format aims to follow `pycodestyle (pep8) default output format
<https://github.com/PyCQA/pycodestyle/blob/master/pycodestyle.py#L108>`_.


- Free software: Apache license
- Documentation: https://docs.openstack.org/bashate
- Source: https://opendev.org/openstack/bashate/
- Bugs: https://bugs.launchpad.net/bash8
- Release notes: https://docs.openstack.org/releasenotes/bashate/index.html
- Contributing: https://docs.openstack.org/bashate/latest/contributor/index.html

Currently Supported Checks
--------------------------

Errors
~~~~~~

Basic white space errors, for consistent indenting

- E001: check that lines do not end with trailing whitespace
- E002: ensure that indents are only spaces, and not hard tabs
- E003: ensure all indents are a multiple of 4 spaces
- E004: file did not end with a newline
- E005: file does not begin with #! or have a .sh prefix
- E006: check for lines longer than 79 columns

Structure Errors
~~~~~~~~~~~~~~~~

A set of rules that help keep things consistent in control blocks.
These are ignored on long lines that have a continuation, because
unrolling that is kind of "interesting"

- E010: *do* not on the same line as *for*
- E011: *then* not on the same line as *if* or *elif*
- E012: heredoc didn't end before EOF
- E020: Function declaration not in format ``^function name {$``

Obsolete, deprecated or unsafe syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rules to identify obsolete, deprecated or unsafe syntax that should
not be used

- E040: Syntax errors reported by `bash -n`
- E041: Usage of $[ for arithmetic is deprecated for $((
- E042: local declaration hides errors
- E043: arithmetic compound has inconsistent return semantics
- E044: Use [[ for =~,<,> comparisions
