import unittest
from misc.shell import shell, ShellException


class ShellTest(unittest.TestCase):

    def test_shell_echo(self):
        out, err = shell('echo hello world!')
        self.assertEqual(out, 'hello world!\n')
        self.assertEqual(err, '')

    def test_bad_command(self):
        with self.assertRaises(OSError):
            shell('bogus_command_oansdi')

    def test_shell_gcloud(self):
        with self.assertRaises(ShellException) as result:
            shell('gcloud')
        e = result.exception
        self.assertEqual(e.commands, ('gcloud',))
        self.assertEqual(e.message, 'Process exited with non-zero error code')
        self.assertEqual(e.stdin, None)
        self.assertEqual(e.context, None)
        self.assertEqual(e.exit_codes, [2])
        self.assertEqual(e.stdout, '')
        # self.assertEqual(e.stderr, '')

    def test_shell_pipe(self):
        out, err = shell('echo one two', "awk '{print $1}'")
        self.assertEqual(out, 'one\n')
        self.assertEqual(err, '')
        out, err = shell('echo one two', "awk '{print $2}'")
        self.assertEqual(out, 'two\n')
        self.assertEqual(err, '')
        out, err = shell('echo one two', "awk '{print $3}'")
        self.assertEqual(out, '\n')
        self.assertEqual(err, '')
