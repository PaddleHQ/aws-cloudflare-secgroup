#!/bin/bash
#
# based on https://github.com/mikedlr/mdd-ansible-dev/blob/master/git-hooks/pre-commit
#
# copyright Michael De La Rue (c) 2017
# copyright Michael De La Rue (c) 2018  - paid work for Paddle.com
#
# This file is licensed under the AGPLv3
find . -type f | ( 
    failcount=0
    substatus=0
    while read -r file
    do
	case "$file" in
	    *.py)
		flake8 --ignore=W503,E402,E501 "$file" && ! grep 'pdb.set_trace\|FIXME' "$file" ;;
	    *.yaml | *.yml )
		yamllint "$file" ;;
	    *.sh)
		shellcheck "$file"
	esac
	newstat=$?
	if [[ "$newstat" -gt "$status" ]]
	then
	    ((failcount++))
	    substatus=$newstat
	fi
    done
    exit $failcount )

status=$?

if [[ "$status" -gt 0 ]]
then
    echo "linting failed on $status files" 
    exit $1
fi
