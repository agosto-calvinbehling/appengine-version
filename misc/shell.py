from subprocess import Popen, PIPE
import json
import shlex


class ShellException(Exception):
    def __init__(self, message, exit_codes=None, stdout=None, stderr=None, stdin=None, commands=None, context=None):
        super(ShellException, self).__init__(message)
        self.commands = commands
        self.context = context
        self.exit_codes = exit_codes
        self.stderr = stderr
        self.stdin = stdin
        self.stdout = stdout

    def __str__(self):
        structured = json.dumps({
            "commands": self.commands,
            "context": self.context,
            "exit_codes": self.exit_codes,
            "stderr": self.stderr,
            "stdin": self.stdin,
            "stdout": self.stdout,
        })
        return '{}: {}'.format(self.message, structured)


def shell(*commands, **kwargs):
    stdin_data = kwargs.pop('stdin_data', None)
    errexit = kwargs.pop('errexit', True)
    pipe_stderr = kwargs.pop('pipe_stderr', True)
    assert len(kwargs) == 0, 'extra args: {}'.format(kwargs)
    stderr_pipe = PIPE if pipe_stderr else None

    procs = []
    for cmd in commands:
        if not procs:
            procs.append(Popen(shlex.split(cmd), stdout=PIPE, stderr=stderr_pipe))
        else:
            procs.append(Popen(shlex.split(cmd), stdout=PIPE, stderr=stderr_pipe, stdin=procs[-1].stdout))
            procs[-2].stdout.close()
    if not procs:
        raise TypeError('shell() requires at least one command to execute')

    stdoutdata, stderrdata = procs[-1].communicate(stdin_data)

    error_codes = []
    for p in reversed(procs):
        p.wait()
        error_codes.insert(0, p.returncode)

    if errexit and any(error_codes):
        msg = 'Process exited with non-zero error code'
        raise ShellException(msg, exit_codes=error_codes, stdout=stdoutdata, stderr=stderrdata, commands=commands, stdin=stdin_data)

    return stdoutdata, stderrdata
