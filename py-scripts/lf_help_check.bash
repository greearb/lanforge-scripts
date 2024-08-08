#!/bin/bash

ANY_FAILED=0
FILES=`ls *.py`
for FILE in $FILES
do
	echo $FILE
	timeout 10 env DISPLAY=:1 python3 ./${FILE} --help > /dev/null
	if [[ $? -eq 0 ]]; then
		echo "PASSED"
	else
		echo "ERROR: FAILED ${FILE}"
		ANY_FAILED=1
	fi
done

if [[ $ANY_FAILED -eq 1 ]]; then
	exit 1
else
	exit 0
fi