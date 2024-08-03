#!/bin/bash

repo_path=$1
script_path=$(dirname $0)

tag_list=$(git -C $repo_path tag -l --sort=-v:refname | grep -E "^[^-]*-[^-]*$")
tag_path=$script_path/../data/tags.txt
echo $tag_list | tr ' ' '\n' > $tag_path