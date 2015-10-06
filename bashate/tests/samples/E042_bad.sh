function hello {
    local foo=$(ls)
}

function hello_too {
    local foo=`ls`
}

hello
hello_too
