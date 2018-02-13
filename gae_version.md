
*Usage*

Run `python gae_version.py` for help.
```
> ./gae_version.py

usage: gae_version.py [-h] [-V VERSION] [-A PROJECT] [-i]
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
> ./gae_version.py help list

list <pattern>Print the version table for the current project
Filter the list by adding a regex pattern
'+' denotes the default version for the module/service
'-' denotes an available version for the module/service

```


### List versions
`python gae_version.py --project <project name> list <pattern>`

```
INDEX  VERSION                                                   frontend  default  refresh  content  migration  backup
0      320-1-7ef044fd58                                          -         -        -
1      320-2-aac3d5f825                                          -         -        -        -        -          -
2      321-0-fff9f9e2ab                                          -         -        -        
3      322-0-c250d16724                                          -         -        -        -        -          -
4      324-0-96f30f94b7                                          -         -        -        -        -          -
5      325-1-28afd7b4fb                                          -         -        -        -        -          -
6      325-2-9be3162894                                          -         -        -        -        -
7      325-3-29bde01e75                                          -         -        -        -        -
8      325-4-dee996d65d                                          -         -        -        -        -          -
9      325-5-a89ccc57f3                                          -         -        -        -        -          -
10     325-6-984089c489                                          -         -        -        -        -          -
11     325-7-47492d95f3                                          -         -        -        -        -          -
12     325-7-545350267a                                          -         -        
13     326-2c22c74d0a                                            -         -        -        -        -          -
14     327-0-9c1016fd1a                                          -         -        -        -        -          -
15     ah-builtin-datastoreservice                               -         
16     ah-builtin-python-bundle                                  -         
17     ereport-test-caedc56daf                                   -         -        -        -        -          -
```

### List versions Filtered
`python gae_version.py --project <project name> list .*fff`

```
INDEX  VERSION           frontend  default  refresh  content  migration  backup
0      320-2-aac3d5f825  -         -        -        -        -          -
1      325-2-9be3162894  -         -        -        -        -
```
