#!/bin/bash
cat versions.json | jq -r '. as $versions
	| $versions
		| [.[]]
		| add
		| unique as $unique
	| $versions
		| with_entries(.value = .value[0])
		| . as $current
	| $versions
		| keys as $modules
	| [foreach $unique as $v (
			{foreach $module as $m (
					{"key": $m, "value": any($versions.$module, $v)}
			)}
		)]
	'