
*Usage*

Run `python gcloud-ae-versions.py` for help.
```
> ./gcloud-ae-versions.py 
usage: gcloud-ae-versions.py [-h] [-V VERSION] [-A PROJECT] [-i]
                             [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                             [commands [commands ...]]

Modify active versions for App Engine.

positional arguments:
  commands              run "? or help" for more info (without --)

optional arguments:
  -h, --help            show this help message and exit
  -V VERSION            Set a specific version
  -A PROJECT, --project PROJECT
                        project
  -i, --interactive     enable interactive mode
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level

Documented commands (type help <topic>):
========================================
EOF  current  fetch  help  list  project  quit  set

```

*Specific command help*

```
> ./gcloud-ae-versions.py help list

list <pattern>Print the version table for the current project
Filter the list by adding a regex pattern
'1' denotes the service version receives all traffic for that service
'0' denotes the service will not receive any traffic for that service
'0.XX' any other number denotes the percentage of traffic a version is serving

```


### List versions
`python gcloud-ae-versions.py --project <project name> list <pattern>`

```
INDEX  VERSION                         frontend  default  refresh  content  migration  backup
0      375-0-3585f2f478                0         0        0        0        0          0     
1      376-0-3bbcbfa308                0         0        0        0        0          0     
2      377-0-7afba020c3                0         0        0        0        0          0     
3      385-1-65fb424471                0         0        0        0        0          0     
4      386-0-2fa061d77a                0         0        0        0        0          0     
5      389-0-7f56ab2141                0         0        0        0        0          0     
6      390-0-9702908981                0         0        0        0        0          0     
7      390-1-e86a3ac7d0                0         0        0        0        0          0     
8      391-0-66770b3ec8                0         0        0        0        0          0     
9      391-1-6303e7bfa5                0         0        0        0        0          0     
10     392-0-5e108887a5                0         0        0        0        0          0     
11     393-0-9475188685                0         0        0        0        0          0     
12     394-0-f4fd114f08                0         0        0        0        0          0     
13     395-0-5336e25a0d                0         0        0        0        0          0     
14     396-0-2a783accc8                0         0        0        0        0          0     
15     397-0-1e70713866                0         0        0        0        0          0     
16     397-1-d08b17b93d                0         0        0        0        0          0     
17     backup-module-update-test                                                       0     
18     content-delete-01-3d02e795e7    0         0        0        0        0          0     
19     displays-limit-300-3d1a58b32d   0         0        0        0        0          0     
20     displays-limit-3d1a58b32d       0         0        0        0        0          0     
21     displays-perf-04-5477325cf3     0         0        0        0        0          0     
22     displaystaterrfix5-510a6df1c0                                                   0     
23     displaystaterrfix7-a092fe9ae4   0         0        0        0        0          0     
24     displaystaterrfix8-cb5e6f968e   0         0        0        0        0          0     
25     displaystaterrfix9-47c0826cc8   0         0        0        0        0          0     
26     jinja-two-test                                                                  0     
27     layout-templates-01-70caec0093  0         0        0        0        0          0     
28     routes-reorg-ef45b2c636         0         0        0        0        0          0     
29     sd-6275-test-29ae4588cf         0         0        0        0        0          0     
30     sd-6541-f9401965f2              0         0        0        0        0          0     
31     sd-6589-test-d16b80369d         0         0        0        0        0          0     
32     sd-6618-bob9-dff77e5a03         0         0        0        0        0          0     
33     sd-7092-03-6e6a211940           0         0        0        0        0          0     
34     sd-7192-01-880b96bd17                     0                 0        0          0     
35     sd-7199-01-c884da6d4b           1         1        1        1        1          1     
36     test-sd-7039-880b96bd17         0         0        0        0        0          0     
```

### List versions Filtered
`python gcloud-ae-versions.py --project <project> list .*88
```
INDEX  VERSION                  frontend  default  refresh  content  migration  backup
0      392-0-5e108887a5         0         0        0        0        0          0     
1      393-0-9475188685         0         0        0        0        0          0     
2      sd-6275-test-29ae4588cf  0         0        0        0        0          0     
3      sd-7192-01-880b96bd17              0                 0        0          0     
4      sd-7199-01-c884da6d4b    1         1        1        1        1          1     
5      test-sd-7039-880b96bd17  0         0        0        0        0          0     
```
