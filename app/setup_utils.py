import os
from setuptools import Command
import shlex
import shutil
import subprocess
import sys
import typing


class CleanCommand(Command):
    """
    Custom clean command to tidy up the project root.
    """
    user_options = [] # type: typing.List[typing.Any]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """modify os command if your build created other resources"""
        directories_to_delete_in_tree = ["build", "__pycache__", ".cache", ".eggs", ".mypy_cache", ".pytest_cache"]
        files_to_delete_in_tree = ['coverage.xml', '.coverage']

        for dirpath, dirnames, filenames in os.walk("."):
            for directory in dirnames:
                if directory in directories_to_delete_in_tree:
                    print("Delete directory %s" % os.path.join(dirpath, directory))
                    shutil.rmtree(os.path.join(dirpath, directory))

            for filename in filenames:
                if filename.endswith(".pyc") or filename in files_to_delete_in_tree:
                    print("Delete file %s" % os.path.join(dirpath, filename))
                    os.remove(os.path.join(dirpath, filename))


class LintCommand(Command):
    """
    Custom setup command to run pylint.
    """
    user_options = [
        ('opts=', None, "Line of options to pass to the pylint runner"),
        ('addopts=', None, "Additional options to combine with options from setup.cfg")
    ]

    def initialize_options(self):
        self.opts = ''
        self.addopts = ''

    def finalize_options(self):
        self.pylint_opts = shlex.split(self.opts) + shlex.split(self.addopts)

    def run(self):
        from pylint.lint import Run as RunPylint
        RunPylint(self.pylint_opts)


class TypecheckCommand(Command):
    """
    Runs mypy - Python type checker.
    Mypy has got its API to run programmatically but other libraries may not, so run as subprocess.
    """
    def initialize_options(self):
        self.packages = ''

    user_options = [
        ('packages=', None, "Additional packages to combine with options from setup.cfg")
    ]

    def finalize_options(self):
        if len(self.packages) > 0:
            package_list = ['--package=' + package for package in self.packages.split()]
            self.packages = " ".join(package_list)

    def run(self):
        subprocess.run('python setup.py clean', shell=True)
        cmd_to_run = 'python -m mypy ' + self.packages
        print(cmd_to_run)
        completed_process = subprocess.run(cmd_to_run, universal_newlines=True, shell=True)
        return_code = completed_process.returncode
        if return_code != 0:
            print("Error: Mypy setup.py command has failed", file=sys.stderr)
            exit(1)
        else:
            print("Success: Mypy hasn't discovered any problems.")
