# for loop examples

# pass
for i in $(seq 1 5); do
    echo $i
done

# pass
for (( i = 0 ; i < 5 ; i++ )); do
    echo $i
done

# fail E010
for i in $(seq 1 5);
do
    echo $i
done

# fail E010
for (( i = 0 ; i < 5 ; i++ ));
do
    echo $i
done

# should ignore "for (" [note single parenthesis] as it is likely awk
awk '{
    for (i = 1; i < 5; i++)
        print $i
}' < /dev/null
