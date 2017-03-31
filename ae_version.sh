#!/bin/bash
set -euo pipefail

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

export VERSIONS=$(appcfg.py "$@" list_versions)

CSV=$(python - <<'____EOF'
import yaml
import json
import os
import csv
import sys
data = yaml.load(os.environ['VERSIONS'])
module_list = data.keys()
current = {k: v[0] for k, v in data.iteritems()}
version_list = sorted(list(set(sum(data.values(), []))))
headers = ['VERSION'] + module_list
result = [headers]
for version in version_list:
    item = [version]
    for m in module_list:
        if version == current[m]:
            item.append('+')
        elif version in data[m]:
            item.append('-')
        else:
            item.append('')
    result.append(item)
csv.writer(sys.stdout).writerows(result)
____EOF
)
echo "$CSV" | column -t -s,
# current=$(echo "$versions" | jq 'with_entries(.value = .value[0])')
# unique=$(echo "$versions" | jq '[.[]] | add | unique')
