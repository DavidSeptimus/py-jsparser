#!/usr/bin/env bash

root=$(PWD)
## could iterate through a bunch of languages here

lang_dir="${root}/languages"
mkdir -p "$lang_dir"

cd "$lang_dir" || echo "${lang_dir} not found" exit 1
rm -rf tree-sitter-javascript
git clone https://github.com/tree-sitter/tree-sitter-javascript
