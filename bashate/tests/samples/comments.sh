#!/bin/bash

# make sure we're ignoring comments correctly

## multiple

# if [ foo ];
# then
#  echo "blah"
# fi

foo=1 # `test`

if [ foo ]; then # hello
    echo "hi"
fi

if [ foo ]; then ## hello ##
    echo "hi"
fi

# ``RST style comment``

 # ``indented comment``

#	tab comment
