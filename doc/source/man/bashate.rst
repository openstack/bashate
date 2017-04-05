===========================
:program:`bashate` man page
===========================

.. program:: bashate
.. highlight:: bash

SYNOPSIS
========

:program:`bashate` [options] <file> [files...]

DESCRIPTION
===========

The :program:`bashate` command line utility is a style-checker for
bash scripts.

The name is derived from :program:`pep8`, a Python lint-type tool.

OPTIONS
=======

--help, -h        Print help
--verbose, -v     Verbose output
--ignore, -i      Tests to ignore, comma separated
--error, -e       Tests to trigger errors instead of warnings, comma separated
--warn, -w        Tests to trigger warnings instead of errors, comma separated

EXAMPLES
========

Run all tests on a single file::

    bashate file.sh

Run tests on several files, while also ignoring several errors::

    bashate -i E010,E011 file.sh file2.sh

BUGS
====

http://bugs.launchpad.net/bash8
