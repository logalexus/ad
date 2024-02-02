#!/usr/bin/env python3

import click
import jinja2
import yaml
from utils import run_command
from vpn_gen import gen

TEMPLATE_PATH = "templates/"
HOSTS_PATH = "ansible/"
CONFIG_PATH = "config.yml"
PRIVATE_KEY_PATH = "../.vagrant/machines/{0}/virtualbox/private_key"

@click.group()
def cli():
    pass


@cli.command(help="Generate infrastructure configs")
def generate():
    teams = yaml.load(open(CONFIG_PATH), Loader=yaml.FullLoader)["teams"]
    for i, team in enumerate(teams):
        team["id"] = f"team{i+1}"
        team["port"] = 2200+i+1
        team["private"] = PRIVATE_KEY_PATH.format(team["id"])
    print(teams)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    vagrant_template = env.get_template(TEMPLATE_PATH + 'Vagrantfile.j2')
    inventory_template = env.get_template(TEMPLATE_PATH + 'inventory.j2')

    with open('Vagrantfile', 'w') as vagrant_file:
        vagrant_file.write(vagrant_template.render(teams=teams))

    with open(HOSTS_PATH + 'inventory.ini', 'w') as inventory_file:
        inventory_file.write(inventory_template.render(teams=teams))
        
    vpn_server = yaml.load(open(CONFIG_PATH), Loader=yaml.FullLoader)["vpn-server"]
    teams = range(1, len(teams) + 1)
    gen.run(teams, 6, vpn_server["ip"])
    


@cli.command(help="Destroy VM")
@click.argument("name")
def destroy(name):
    cmd = ["vagrant", "destroy", "-f", "--parallel", name]
    run_command(cmd)


@cli.command(help="Destroy all VMs")
def destroyall():
    cmd = ["vagrant", "destroy", "-f", "--parallel"]
    run_command(cmd)


@cli.command(help="UP all VMs")
def up():
    cmd = ["vagrant", "up", "--parallel"]
    run_command(cmd)


@cli.command(help="Reload VM")
@click.argument("name")
def reload(name):
    cmd = ["vagrant", "reload", name]
    run_command(cmd)


if __name__ == "__main__":
    cli()
