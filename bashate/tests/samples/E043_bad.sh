count=0
things="0 1 0 0 1"

for i in $things; do
    if [ $i == "1" ]; then
        (( count++ ))
    fi
done

echo "Count is ${count}"
