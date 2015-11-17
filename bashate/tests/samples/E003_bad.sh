#!/bin/bash

this is \
      bad continuation as it does not match 1st arg or %4

a \
 bad indent

if foo; then
    testing a \
  bad indent, indented
fi
