===============================
bashate
===============================

A pep8 equivalent for bash scripts

This program attempts to be an automated style checker for bash scripts
to fill the same part of code review that pep8 does in most OpenStack
projects. It started from humble beginnings in the DevStack project,
and will continue to evolve over time.

- Free software: Apache license
- Documentation: http://docs.openstack.org/developer/bashate
- Source: http://git.openstack.org/cgit/openstack-dev/bashate
- Bugs: http://bugs.launchpad.net/bash8

Currently Supported Checks
--------------------------

Errors
~~~~~~

Basic white space errors, for consistent indenting

- E001: check that lines do not end with trailing whitespace
- E002: ensure that indents are only spaces, and not hard tabs
- E003: ensure all indents are a multiple of 4 spaces
- E004: file did not end with a newline

Structure Errors
~~~~~~~~~~~~~~~~

A set of rules that help keep things consistent in control blocks.
These are ignored on long lines that have a continuation, because
unrolling that is kind of "interesting"

- E010: *do* not on the same line as *for*
- E011: *then* not on the same line as *if* or *elif*
- E012: heredoc didn't end before EOF
- E020: Function declaration not in format ``^function name {$``

Obsolete and deprecated syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rules to identify obsolete and deprecated syntax that should not be used

- E041: Usage of $[ for arithmetic is deprecated for $((

See also
~~~~~~~~

See also :doc:`/man/bashate`.
