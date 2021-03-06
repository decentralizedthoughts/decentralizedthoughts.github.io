#!/bin/bash

scriptdir=$(cd $(dirname $0); pwd -P)
postdir="$scriptdir/"
line=1

is_number()
{
    local re='^[0-9]+$'
    if [[ "$1" =~ $re ]] ; then
        return 1
    else
        return 0
    fi
}

files=`cd $postdir && find . -name "*.md" && find . -name "*.markdown"`

files=`echo "$files" | grep -v "/files/"`
files=`echo "$files" | grep -v "/templ.md" | grep -v "/bib.md"`

files=`echo "$files" | cut -c 3-` # cuts the first two characters (i.e., the ./)

files=`echo "$files" | sort`

sorted_files=`echo "$files" | sort -r`

titles=`grep '^title:' $sorted_files | cut -f 3 -d':'`

if [ "$1" == "l" -o "$1" == "list" -o "$1" == "-l" ]; then
    echo "$titles" | awk '{printf "%d\t%s\n", NR, $0}'
else
    line=$1
    if [ -z "$line" ]; then
        line=1
    elif is_number "$line"; then
        echo "ERROR: '$line' is not a number"
        exit 1
    fi
    files=`echo "$files" | tail -n "$line"`
    file=`echo "$files" | head -n 1`

    vim "$postdir/$file"
fi

