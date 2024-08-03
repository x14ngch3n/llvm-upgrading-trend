#!/bin/bash

old_tag=$1
new_tag=$2
file_path=$3
repo_path=$4
script_path=$(dirname $0)

diff_stat=$(git -C $repo_path diff --stat $old_tag $new_tag $file_path | tail -n1)

insertions=$(echo $diff_stat | cut -d "," -f 2 | grep -oE "[0-9]+")
if [ -z $insertions ]; then
    insertions=0
fi

deletions=$(echo $diff_stat | cut -d "," -f 3 | grep -oE "[0-9]+")
if [ -z $deletions ]; then
    deletions=0
fi

changes=$(($insertions + $deletions))

csv_path=$script_path/../data/$(basename $file_path).csv
if [ ! -f $csv_path ]; then
    touch $csv_path
fi

echo $old_tag, $new_tag, $insertions, $deletions, $changes >> $csv_path