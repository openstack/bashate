function hello {
    local foo=$(ls)
}

function hello_too {
    local foo=`ls`
}

function hello_with_quotes {
    local foo="$(ls)"
    local bar="`ls`"
}

hello
hello_too
