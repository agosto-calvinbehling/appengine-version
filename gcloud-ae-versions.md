
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
`python gcloud-ae-versions.py --project <project> list .*88`
```
INDEX  VERSION                  frontend  default  refresh  content  migration  backup
0      392-0-5e108887a5         0         0        0        0        0          0     
1      393-0-9475188685         0         0        0        0        0          0     
2      sd-6275-test-29ae4588cf  0         0        0        0        0          0     
3      sd-7192-01-880b96bd17              0                 0        0          0     
4      sd-7199-01-c884da6d4b    1         1        1        1        1          1     
5      test-sd-7039-880b96bd17  0         0        0        0        0          0     
```

### Set version
`python gcloud-ae-versions.py --project <project name> set <pattern>`
```
> ./gcloud-ae-versions.py -A <PROJECT> set sd-7199

2018-02-12 18:35:06,299 gcloud-ae-versions.py:191 version: sd-7199-01-c884da6d4b
Setting the following traffic allocations:
 - <PROJECT>/backup/sd-7199-01-c884da6d4b: 1.0
 - <PROJECT>/content/sd-7199-01-c884da6d4b: 1.0
 - <PROJECT>/default/sd-7199-01-c884da6d4b: 1.0
 - <PROJECT>/frontend/sd-7199-01-c884da6d4b: 1.0
 - <PROJECT>/migration/sd-7199-01-c884da6d4b: 1.0
 - <PROJECT>/refresh/sd-7199-01-c884da6d4b: 1.0
Any other versions on the specified services will receive zero traffic.
Waiting for operation [apps/<PROJECT>/operations/69438ddd-da91-4e49-864f-bca4e42ba085] to complete...done.
Waiting for operation [apps/<PROJECT>/operations/604582c6-f150-4083-93ac-2d0896c9871e] to complete...done.
Waiting for operation [apps/<PROJECT>/operations/81759bfa-0298-4545-9e54-9c18c99987b1] to complete...done.
Waiting for operation [apps/<PROJECT>/operations/221c6222-24aa-4f37-9853-d6cbe07a33a7] to complete...done.
Waiting for operation [apps/<PROJECT>/operations/7a5d64ed-e526-48f8-b355-19df010819d8] to complete...done.
Waiting for operation [apps/<PROJECT>/operations/6251aff8-82c4-4f2a-8daa-e115ae2c02d7] to complete...done.
```

### Interactive mode
`python gcloud-ae-versions.py -i`
```
Select a project: "project <gcp project name>"
Then list available versions/service with "list"
"help" will list additional commands and how to use them

(no project)> project skykit-display
(skykit-display)> list
INDEX  VERSION                   default
0      23-57a6b55c49             0      
1      24-dbf13faceb             0      
2      25-e3306843f8             0      
3      27-0606759d38             0      
4      30-5aeea914f7             0      
5      31-273e9364d9             0      
6      33-bfd7f715eb             0      
7      34-224a0c259e             0      
8      35-d9817365f0             0      
9      36-d9d020dbd6             0      
10     38-28b4c9b450             0      
11     40-c0abe63528             0      
12     41-66cce4c95a             0      
13     44-7c79eed8b9             1      
14     44-karlk-7c79eed8b9       0      
15     bootstraptest-689b033153  0      
16     bootstraptest-9b6146235b  0      
(skykit-display)> quit

goodbye
```
