#!/bin/bash

if [ ! -f pcdshub_repos.json ]; then
  gh repo list pcdshub --limit 1000 --json name >pcdshub_repos.json
fi

pcdshub_repos=$(jq -r 'map(.name)[]' <pcdshub_repos.json | sort)
for name in $pcdshub_repos; do
  if [[ $name =~ lcls-plc-* || $name =~ lcls-twincat-* ]]; then
    if [ ! -d $name ]; then
      git submodule add https://github.com/pcdshub/$name
    fi
  fi
done
