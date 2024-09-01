import subprocess
import sys
from typing import List
import click
import secrets
import string


def run_command(command: List[str], cwd=None, env=None):
    print_bold(f'Running command {command}')
    p = subprocess.run(command, cwd=cwd, env=env)
    if p.returncode != 0:
        print_error(f'Command {command} failed!')
        sys.exit(1)


def print_error(message: str):
    click.secho(message, fg='red', err=True)


def print_success(message: str):
    click.secho(message, fg='green', err=True)


def print_bold(message: str):
    click.secho(message, bold=True, err=True)


def generate_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password
