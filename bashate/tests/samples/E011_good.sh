#!/bin/bash

# E011 good
if [ 0 ]; then
    run_morethings
else
    run_otherthings
fi

# E011 with comment
if [ 0 ]; then # comment
    run_morethings
fi
