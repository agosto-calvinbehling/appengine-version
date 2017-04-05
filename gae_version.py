#!/usr/bin/python

from cmd import Cmd as Repltool
from StringIO import StringIO
from subprocess import Popen, PIPE
import argparse
import csv
import logging
import sys
import yaml
import re


# Resources:
# https://docs.python.org/2/library/argparse.html?highlight=py%20args#module-argparse
# https://docs.python.org/2/library/cmd.html
# https://pymotw.com/2/cmd/

TEST_DATA = {'content': ['320-2-aac3d5f825', '300-hotfix2-864a8314e6', '310-2-af8ce4c702', '312-4-02417e1466', '313-8-9a0d6a0554', '313-9-9f65c9cdcb', '320-1-7ef044fd58', '325-1-28afd7b4fb', '325-2-9be3162894', '325-3-29bde01e75'], 'frontend': ['320-2-aac3d5f825', '313-8-9a0d6a0554', '313-87157e1d55', '313-9-9f65c9cdcb', '320-1-7ef044fd58', '325-1-28afd7b4fb', '325-2-9be3162894', '325-3-29bde01e75'], 'migration': ['320-2-aac3d5f825', '300-hotfix2-864a8314e6', '310-2-af8ce4c702', '312-4-02417e1466', '313-8-9a0d6a0554', '313-87157e1d55', '313-9-9f65c9cdcb', '320-1-7ef044fd58', '325-1-28afd7b4fb', '325-2-9be3162894', '325-3-29bde01e75'], 'default': ['320-2-aac3d5f825', '300-hotfix2-864a8314e6', '310-2-af8ce4c702', '312-4-02417e1466', '313-8-9a0d6a0554', '313-9-9f65c9cdcb', '320-1-7ef044fd58', '325-1-28afd7b4fb', '325-2-9be3162894', '325-3-29bde01e75', 'ah-builtin-datastoreservice', 'ah-builtin-python-bundle', 'ah-builtin-python-bundle'], 'backup': ['320-2-aac3d5f825', '300-hotfix2-864a8314e6', '310-2-af8ce4c702', '312-4-02417e1466', '313-8-9a0d6a0554', '313-9-9f65c9cdcb', '320-1-7ef044fd58', '325-1-28afd7b4fb', '325-2-9be3162894', '325-3-29bde01e75'], 'refresh': ['320-2-aac3d5f825', '320-1-7ef044fd58', '325-1-28afd7b4fb', '325-2-9be3162894', '325-3-29bde01e75']}
TEST_DATA_ARRAY = [['VERSION', 'content', 'frontend', 'migration', 'default', 'backup', 'refresh'], ['300-hotfix2-864a8314e6', '-', '', '-', '-', '-', ''], ['310-2-af8ce4c702', '-', '', '-', '-', '-', ''], ['312-4-02417e1466', '-', '', '-', '-', '-', ''], ['313-8-9a0d6a0554', '-', '-', '-', '-', '-', ''], ['313-87157e1d55', '', '-', '-', '', '', ''], ['313-9-9f65c9cdcb', '-', '-', '-', '-', '-', ''], ['320-1-7ef044fd58', '-', '-', '-', '-', '-', '-'], ['320-2-aac3d5f825', '+', '+', '+', '+', '+', '+'], ['325-1-28afd7b4fb', '-', '-', '-', '-', '-', '-'], ['325-2-9be3162894', '-', '-', '-', '-', '-', '-'], ['325-3-29bde01e75', '-', '-', '-', '-', '-', '-'], ['ah-builtin-datastoreservice', '', '', '', '-', '', ''], ['ah-builtin-python-bundle', '', '', '', '-', '', '']]


def _abort(msg, exit_code=1):
    sys.stderr.write(msg + '\n')
    sys.exit(exit_code)


def shell(*args, **kwargs):
    kwargs.setdefault('stdout', PIPE)
    check_exit = kwargs.pop('check_exit', True)
    proc = Popen(args, **kwargs)
    result = proc.communicate()[0].strip()
    if check_exit and proc.returncode != 0:
        msg = 'command {} returned with non-zero exit code: {}'.format(args, proc.returncode)
        _abort(msg, proc.returncode)
    return result


def multishell(*args, **kwargs):
    procs = []
    for cmd in args:
        if not procs:
            procs.append(Popen(cmd, stdout=PIPE))
        else:
            procs.append(Popen(cmd, stdout=PIPE, stdin=procs[-1].stdout))
    return procs[-1].communicate()[0].strip()


def generate_table(csv_data):
    return multishell(['echo', csv_data], ['column', '-t', '-s,'])


def fetch_data(project, *args, **kwargs):
    expect_errors = kwargs.pop('expect_errors', False)
    cmd_args = ['-A', project] if project else ['.']
    cmd_args += args
    yaml_data = shell('appcfg.py', 'list_versions', *cmd_args, check_exit=(not expect_errors))
    result = yaml.load(yaml_data)
    if not expect_errors and not result:
        _abort('fetch returned no data')
    return result


def print_data_table(data, current):
    result = generate_human_array(data, current)
    csv_data = to_csv(result)
    output = generate_table(csv_data)
    print(output)


def set_version(project, version_string, modules, *args):
    """
        set_default_version: Set the default (serving) version.
        start_module_version: Start a module version.
        stop_module_version: Stop a module version.
        rollback: Rollback an in-progress update.
    """
    appcfg_cmd = ['appcfg.py', 'set_default_version', '-V', version_string, '-A', project]
    appcfg_args = list(*args)
    for m in modules:
        logging.debug(appcfg_cmd + appcfg_args)
        shell(*(appcfg_cmd + ['-M', m]))


def regex_set_all(project, version_data, version_pattern):
    filtered_data = filter_data(version_data, version_pattern)
    modules = []
    matched_version = None
    for module, version_list in filtered_data.iteritems():
        logging.debug('module: {}'.format(module))
        logging.debug('versions: {}'.format(version_list))
        assert len(version_list) <= 1, 'Ambiguous version expression: {}'.format(version_pattern)
        if len(version_list):
            matched_version = version_list[0]
            modules += [module]
    assert matched_version, 'No module contained a version matching: {}'.format(version_pattern)
    set_version(project, matched_version, modules)


def filter_data(version_data, version_pattern):
    re_version = re.compile(version_pattern)
    return {module: filter(re_version.match, version_list) for module, version_list in version_data.iteritems()}


def validate_version(version, version_data, assert_valid=True, exclude_modules=None):
    exclude_modules = exclude_modules if exclude_modules else []
    for module, version_list in version_data.iteritems():
        if module in exclude_modules:
            continue
        if version not in version_list:
            _abort('module {} does not have version {}'.format(module, version))
            return False
    return True


def filter_current(data):
    return {k: v[0] for k, v in data.iteritems()}


def generate_human_array(data, current):
    module_list = data.keys()
    version_list = sorted(list(set(sum(data.values(), []))))
    headers = ['INDEX', 'VERSION'] + module_list
    result = [headers]
    for idx, version in enumerate(version_list):
        item = [idx, version]
        for m in module_list:
            if version == current[m]:
                item.append('+')
            elif version in data[m]:
                item.append('-')
            else:
                item.append('')
        result.append(item)
    return result


def to_csv(array2d):
    csv_output = StringIO()
    csv.writer(csv_output).writerows(array2d)
    csv_output.seek(0)
    return '{}'.format(csv_output.buf)


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    OFF = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def set_version_parser():
    parser = argparse.ArgumentParser(description='Set versions')
    parser.add_argument('--exclude', dest='exclude', action='append', help='Modules to exclude')
    parser.add_argument('--include', dest='include', action='append', help='Modules to include, defaults to all modules')
    parser.add_argument('version', nargs=1, help='version to include. Requires enough data to uniquely identify the version from the list')


class VersionCmd(Repltool):
    intro = bcolors.HEADER + 'Select a project: "project <gcp project name>"\n'\
        + 'Then list available versions/modules with "list"\n'\
        + '"help" will list additional commands and how to use them\n'\
        + bcolors.OFF
    _set_parser = set_version_parser()

    """ AppEngine Version tool """
    def __init__(self, **kwargs):
        Repltool.__init__(self)
        # self.use_rawinput = False
        self._appcfg_args = kwargs.pop('appcfg_args')
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
            color = bcolors.GREEN
        else:
            project_str = 'no project'
            color = bcolors.RED
        return '{}({})> {}'.format(color, project_str, bcolors.OFF)

    def do_project(self, project_id):
        """project <gcp project id>: Sets the current project"""
        if not project_id:
            return self.do_help('help project')
        new_data = fetch_data(project_id, expect_errors=True)
        if not new_data:
            print('invalid project')
            return
        self._project = project_id
        self._data = new_data

    def do_quit(self, line):
        """Quit the program"""
        print('\ngoodbye')
        return True

    def do_list(self, pattern):
        if not self._project:
            print('requires an active project; see "help project"')
            return
        if not self._data:
            self._data = fetch_data(self._project, expect_errors=True)
        if self._data:
            current = filter_current(self._data)
            filtered = filter_data(self._data, pattern)
            logging.debug(filtered)
            print_data_table(filtered, current)
            return
        print('failed to fetch data')

    def help_list(self):
        print('\n'.join([
            "list <pattern>"
            "Print the version table for the current project",
            "Filter the list by adding a regex pattern",
            "'+' denotes the default version for the module/service",
            "'-' denotes an available version for the module/service",
        ]))

    def do_fetch(self, *args):
        """fetch new version data"""
        if not self._project:
            print('requires an active project; see "help project"')
            return
        self._data = fetch_data(self._project, expect_errors=True)
        if self._data:
            return
        print('failed to fetch data')

    def do_current(self, *args):
        """List current version"""
        if not self._project:
            print('requires an active project; see "help project"')
            return
        if not self._data:
            self._data = fetch_data(self._project, expect_errors=True)
        if self._data:
            current = filter_current(self._data)
            print_data_table(current, current)
        print('failed to fetch data')

    def do_set(self, pattern):
        # import shelex
        # args = shelex.split(pattern)
        # result = self._set_parser.parse(args)
        try:
            regex_set_all(self._project, self._data, pattern)
        except AssertionError as e:
            print(e)
        self._data = fetch_data(self._project, expect_errors=True)

    def help_set(self):
        print('\n'.join([
            "set <pattern>",
            "Set the current version based on the given regular expression.",
            "Will set the version ALL modules.",
            "MUST match at most one version in ALL modules.",
            "MUST match at least one version in ANY module.",
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
    parser = argparse.ArgumentParser(description='Modify active versions for App Engine.')
    parser.add_argument('-V', dest='version', help='Set a specific version')
    parser.add_argument('-A', '--project', dest='project', action='store', help='project')
    parser.add_argument('-i', '--interactive', dest='repl', action='store_true', help='enable interactive mode')

    parser.add_argument('-l', '--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the logging level')
    parser.add_argument('commands', nargs='*', help='run "? or help" for more info (without --)')
    args_namespace = parser.parse_known_args(sys.argv[1:])

    log_level = args_namespace[0].log_level
    if log_level:
        logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)d %(message)s', level=getattr(logging, log_level))

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
