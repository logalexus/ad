#!/usr/bin/env python3

import click
import jinja2
import yaml
from utils import run_command

TEMPLATE_PATH = "templates/"
HOSTS_PATH = "ansible/"
CONFIG_PATH = 


@click.group()
def cli():
    pass


@cli.command(help="Generate infrastructure configs")
def generate():
    teams = yaml.load(open('config.yml'), Loader=yaml.FullLoader)["teams"]
    for i, team in enumerate(teams):
        team["id"] = f"team{i+1}"
        team["port"] = 1000+i
        team["private"] = f".vagrant/machines/{team['id']}/virtualbox/private_key"
    print(teams)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    vagrant_template = env.get_template(TEMPLATE_PATH + 'Vagrantfile.j2')
    inventory_template = env.get_template(TEMPLATE_PATH + 'inventory.j2')

    with open('Vagrantfile', 'w') as vagrant_file:
        vagrant_file.write(vagrant_template.render(teams=teams))

    with open(HOSTS_PATH + 'inventory.ini', 'w') as inventory_file:
        inventory_file.write(inventory_template.render(teams=teams))


@cli.command(help="Destroy VM")
@click.argument("name")
def destroy(name):
    cmd = ["vagrant", "destroy", name]
    run_command(cmd)


@cli.command(help="Destroy all VMs")
def destroyall():
    cmd = ["vagrant", "destroy"]
    run_command(cmd)


@cli.command(help="UP all VMs")
def up():
    cmd = ["vagrant", "up"]
    run_command(cmd)


@cli.command(help="Reload VM")
@click.argument("name")
def reload(name):
    cmd = ["vagrant", "reload", name]
    run_command(cmd)


if __name__ == "__main__":
    cli()
