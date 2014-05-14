#!/bin/bash
# E020
function somefunction () {
	echo "E002: Has a tab"

  echo "E003: Not an indent with multiple of 4"
}

# E001
somefunction args  

# E010
for thing in things
do
    run_things thing
done

while 0
do
    run_thing
done

until 1
do
    run_thing
done

# E011
if [ 0 ]
then
    run_morethings
else
    run_otherthings
fi

# E012
cat <<EOH
this heredoc is bad

# E004