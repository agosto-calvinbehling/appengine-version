#!/bin/bash
set -euo pipefail
set -x

[ -z "$(which 'jq')" ] && {
	>&2 echo 'requires jq: https://stedolan.github.io/jq/'
	exit 1
}

[ -z "$(which 'python')" ] && {
	>&2 echo 'requires python'
	exit 1
}


PROJECT="${1}"

yaml2json='python -c '"'"'import yaml, json, sys; data = yaml.load(sys.stdin.read()); print(json.dumps(data))'"'"

versions=$(appcfg.py "$@" list_versions | eval "${yaml2json}")
current=$(echo "$versions" | jq 'with_entries(.value = .value[0])')
unique=$(echo "$versions" | jq '[.[]] | add | unique')
