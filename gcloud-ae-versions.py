#!/usr/bin/python
import sys
sys.path.insert(0, './lib')

from cmd import Cmd as Repltool
from decimal import Decimal
from misc.column import column
from misc.groupby import groupby, multi_groupby, multi_groupby_single_value, get_nested_value
from misc.shell import shell, ShellException
from misc.which import which
import argparse
import color
import json
import logging
from functools import wraps
import re

KEY_VERSION = 'id'
KEY_SERVICE = 'service'
KEYS_INSTANCE_CLASS = ('version', 'instanceClass')
KEY_TRAFFIC_SPLIT = 'traffic_split'

FORMAT_JSON = 'json'
FORMAT_CSV = 'csv'
FORMAT_TABLE = 'table'
FORMAT_LIST = [FORMAT_JSON, FORMAT_CSV, FORMAT_TABLE]

VERSION_MIGRATE = 'migrate'
VERSION_START = 'start'
VERSION_COMMANDS = [VERSION_MIGRATE, VERSION_START]

SPLIT_BY_COOKIE = 'cookie'
SPLIT_BY_IP = 'ip'
SPLIT_BY_CHOICES = [SPLIT_BY_COOKIE, SPLIT_BY_IP]


def require_project(method):
    @wraps(method)
    def _(self, *args, **kwargs):
        if getattr(self, '_project', None):
            return method(self, *args, **kwargs)
        logging.warn('requires an active project; see "help project"')
    return _


def require_data(method):
    @wraps(method)
    def _(self, *args, **kwargs):
        if not getattr(self, '_data', None):
            self._data = gcloud_fetch_list(self._project)
        if getattr(self, '_data', None):
            method(self, *args, **kwargs)
        else:
            logging.warn('failed to fetch data')
    return _


def new_parser():
    parser = argparse.ArgumentParser(description='Modify active versions for App Engine.')
    parser.add_argument('-V', dest='version', help='Set a specific version')
    parser.add_argument('-A', '--project', dest='project', action='store', help='project')
    parser.add_argument('-i', '--interactive', dest='repl', action='store_true', help='enable interactive mode')

    parser.add_argument('-l', '--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the logging level')
    parser.add_argument('commands', nargs='*', help='run "? or help" for more info (without --)')
    return parser


def repl_cmds(repl):
    names = repl.get_names()
    cmds_doc = []
    cmds_undoc = []
    help = {}
    for name in names:
        if name[:5] == 'help_':
            help[name[5:]] = 1
    names.sort()
    # There can be duplicates if routines overridden
    prevname = ''
    for name in names:
        if name[:3] == 'do_':
            if name == prevname:
                continue
            prevname = name
            cmd = name[3:]
            if cmd in help:
                cmds_doc.append(cmd)
                del help[cmd]
            elif getattr(repl, name).__doc__:
                cmds_doc.append(cmd)
            else:
                cmds_undoc.append(cmd)
    return cmds_doc, cmds_undoc


def gcloud_fetch_list(project):
    out, err = shell('gcloud --format=json --project {} app versions list'.format(project))
    if err:
        logging.error(err.strip())
    return json.loads(out)


def version_table(raw, key=KEY_TRAFFIC_SPLIT):
    data = multi_groupby(raw, KEY_SERVICE, KEY_VERSION)
    service_list = data.keys()
    version_set = set().union(*data.values())

    headers = ['INDEX', 'VERSION'] + service_list
    result = [[color.bold(str(item)) for item in headers]]
    for idx, version in enumerate(sorted(version_set)):
        active = False
        item = [color.grayscale[10](str(idx)), version]
        for service in service_list:
            if version in data[service]:
                assert len(data[service][version]) == 1
                value = data[service][version][0][key]
                if isinstance(value, float):
                    value = Decimal(value).normalize()
                    if value > 0:
                        value = color.red(str(value))
                        active = True
                if not isinstance(value, basestring):
                    value = str(value)
                item.append(value)
            else:
                item.append('')
        if active:
            item[1] = color.red(version)
        result.append(item)
    return result


def filter_current(raw, key=KEY_TRAFFIC_SPLIT):
    return [item for item in raw if item[key] > 0]


def _gcloud_set_version(project, services, version_string, cmd=VERSION_MIGRATE):
    assert cmd in VERSION_COMMANDS
    for service in services:
        command = 'gcloud --project {} --quiet app versions {} --service {} {}'.format(project, cmd, service, version_string)
        try:
            logging.debug(command)
            out, err = shell(command, pipe_stderr=False)
            if out.strip():
                print(out.strip())
        except ShellException as e:
            logging.error(command)
            logging.error(e)
    return out


def gcloud_set_traffic(project, version_weight_dict, services=None, split_by=SPLIT_BY_COOKIE, migrate=False):
    """
        Splits traffic across given services (or all versions if none provided)
        migrate requires warmup to be enabled
        gcloud app services set-traffic --help
    """
    assert split_by in SPLIT_BY_CHOICES
    assert len(version_weight_dict) > 0
    if services:
        services = ' '.join(services) if isinstance(services, [list, set]) else services
    else:
        services = ''
    splits = ','.join(['{}={}'.format(version, weight) for version, weight in version_weight_dict.iteritems()])
    migrate_flag = '--migrate' if migrate else ''
    command = 'gcloud --quiet --project {} app services set-traffic {} --splits {} {}'.format(project, services, splits, migrate_flag)
    try:
        logging.debug(command)
        shell(command, pipe_stderr=False)
    except ShellException as e:
        logging.error(command)
        logging.error(e)
        return False
    return True


def gcloud_set_version(project, data, version_string):
    F = [item[KEY_SERVICE] for item in data if get_nested_value(item, *KEYS_INSTANCE_CLASS).startswith('F')]
    B = [item[KEY_SERVICE] for item in data if get_nested_value(item, *KEYS_INSTANCE_CLASS).startswith('B')]
    _gcloud_set_version(project, B, version_string, cmd='start')
    _gcloud_set_version(project, F, version_string, cmd='migrate')


def regex_set_all(project, version_data, version_pattern):
    filtered_data = filter_data(version_data, version_pattern, KEY_VERSION)
    version_set = {item[KEY_VERSION] for item in filtered_data}
    num_versions = len(version_set)
    assert num_versions <= 1, 'Ambiguous version expression: {}'.format(version_pattern)
    assert num_versions > 0, 'No service contained a version matching: {}'.format(version_pattern)
    version = version_set.pop()
    logging.info('version: {}'.format(version))
    return gcloud_set_traffic(project, {version: 1})


def has_warmup(data):
    """ checks that all elements in list are version dictionaries with warmup enabled """
    return all(['INBOUND_SERVICE_WARMUP' in get_nested_value(item, 'version', 'inboundServices', default=()) for item in data])


def filter_data(version_data, version_pattern, *keys):
    """ Regex filter on list of dictionaries by nested keys """
    re_version = re.compile(version_pattern)
    return [item for item in version_data if re_version.match(get_nested_value(item, *keys))]


class VersionCmd(Repltool):
    intro = color.magenta('Select a project: "project <gcp project name>"\n' +
        'Then list available versions/service with "list"\n' +
        '"help" will list additional commands and how to use them\n')
    # _set_parser = set_version_parser()

    """ AppEngine Version tool """
    def __init__(self, **kwargs):
        Repltool.__init__(self)
        # self.use_rawinput = False
        self._data = kwargs.pop('data', None)
        self._project = None
        project = kwargs.pop('project', None)
        if project:
            self.do_project(project)
        self._history = []

    @property
    def prompt(self):
        if self._project:
            project_str = self._project
            color_fn = color.blue
        else:
            project_str = 'no project'
            color_fn = color.red
        return color_fn('({})> '.format(project_str))

    def do_project(self, project_id):
        """project <gcp project id>: Sets the current project"""
        if not project_id:
            return self.do_help('help project')
        new_data = gcloud_fetch_list(project_id)
        if not new_data:
            print('invalid project')
            return
        self._project = project_id
        self._data = new_data

    def do_quit(self, line):
        """Quit the program"""
        print('\ngoodbye')
        return True

    @require_project
    @require_data
    def do_list(self, pattern):
        data = filter_data(self._data, pattern, KEY_VERSION)
        table = version_table(data)
        columnized = column(table)
        # alternating row colors
        # result = [color.grayscale_bg[1](row) if idx % 2 else row for idx, row in enumerate(columnized)]
        result = columnized
        print('\n'.join(result))

    def help_list(self):
        print('\n'.join([
            "list <pattern>"
            "Print the version table for the current project",
            "Filter the list by adding a regex pattern",
            "'1' denotes the service version receives all traffic for that service",
            "'0' denotes the service will not receive any traffic for that service",
            "'0.XX' any other number denotes the percentage of traffic a version is serving"
        ]))

    @require_project
    def do_fetch(self, *args):
        """fetch new version data"""
        self._data = gcloud_fetch_list(self._project)
        if not self._data:
            logging.warn('failed to fetch data')

    @require_project
    @require_data
    def do_current(self, *args):
        """List current version"""
        current = filter_current(self._data)
        saved = self._data
        self._data = current
        self.do_list(*args)
        self._data = saved

    @require_project
    @require_data
    def do_set(self, pattern):
        try:
            regex_set_all(self._project, self._data, pattern)
        except AssertionError as e:
            print(e)
        self._data = gcloud_fetch_list(self._project)

    def help_set(self):
        print('\n'.join([
            "set <pattern>",
            "Set a version to receive ALL traffic destined to that service",
            "Will set the version ALL services.",
            "MUST match at most one version in ALL services.",
            "MUST match at least one version in ANY service.",
            "Use `list` to see what versions your filter matches.",
        ]))

    def emptyline(self):
        """Don't do anything if user submits an empty line"""
        pass

    def do_EOF(self, line):
        """Use `ctrl+d` to quit"""
        return self.do_quit(line)

    def default(self, line):
        """Print help if nothing is entered"""
        Repltool.default(self, line)
        self.do_help('')


if __name__ == "__main__":
    parser = new_parser()
    args_namespace = parser.parse_known_args(sys.argv[1:])

    log_level = args_namespace[0].log_level
    if log_level:
        logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)d %(message)s', level=getattr(logging, log_level))

    if not which('gcloud'):
        logging.info("Requires 'gcloud'. Install the appengine sdk: https://cloud.google.com/sdk/downloads")
        sys.exit(1)

    appcfg_args = args_namespace[1]
    kwargs = vars(args_namespace[0])
    kwargs.setdefault('appcfg_args', appcfg_args)
    if len(kwargs['commands']):
        commands = ' '.join(kwargs['commands'])
        result = VersionCmd(**kwargs).onecmd(commands)
    elif kwargs['repl']:
        VersionCmd(**kwargs).cmdloop()
    else:
        parser.print_help()
        VersionCmd(**kwargs).onecmd('help')
