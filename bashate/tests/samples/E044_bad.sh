# =~

if [ "test" =~ "]" ]; then
    echo "Does not work!"
fi

[ "test" =~ "string" ] && echo "Does not work!"

if [[ $foo == bar || "test" =~ "[" ]]; then
    echo "Does work!"
fi

[[ "test" =~ "string" ]] && echo "Does work"

# <

if [ 1 < '2' ]; then
    echo "Does not work!"
fi

[ 1 < 2 ] && echo "Does not work!"

if [[ 1 < 2 ]]; then
    echo "Does work!"
fi

[[ 1 < 2 ]] && echo "Does work"

# >

if [ 1 > 2 ]; then
    echo "Does not work!"
fi

[ 1 > 2 ] && echo "Does not work!"

if [[ 1 > 2 ]]; then
    echo "Does work!"
fi

[[ 1 > 2 ]] && echo "Does work"
