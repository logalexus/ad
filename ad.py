#!/usr/bin/env python3

import os
import click
import jinja2
import yaml
from utils import generate_password, run_command
from vpn_gen import gen
from pathlib import Path
import json
import logging
import shutil

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

BASE_PATH = Path(".")
TERRAFORM_PATH = BASE_PATH / "terraform" / "ad"
TEMPLATE_PATH = BASE_PATH / "templates"
ANSIBLE_PATH = BASE_PATH / "ansible"
CONFIG_PATH = BASE_PATH / "config.yml"
RESULT_PATH = BASE_PATH / "result"
TOKENS_PATH = BASE_PATH / "tokens.txt"


def load_config(config_path):
    logging.info(f"Loading configuration from {config_path}")
    with open(config_path) as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


def setup_environment(base_path):
    logging.info(f"Setting up Jinja2 environment with base path {base_path}")
    return jinja2.Environment(loader=jinja2.FileSystemLoader(str(base_path)))


def generate_team_data(config):
    teams = config.get("teams", [])
    public_ips = get_public_ips(TERRAFORM_PATH, "module.vuln")
    for i, team in enumerate(teams):
        team["id"] = f"team{i+1}"
        team['ip'] = f"10.{80 + (i+1) // 256}.{(i+1) % 256}.2"
        team['public_ip'] = public_ips.get(team["id"])
        if "root_password" not in team:
            team['root_password'] = generate_password()
    logging.info("Generated team data")
    return teams


def write_yaml_config(config, config_path):
    logging.info(f"Writing configuration to {config_path}")
    with open(config_path, "w") as outfile:
        yaml.dump(config, outfile, default_flow_style=False, sort_keys=False)


def write_inventory_file(env, template_path, ansible_path, teams, vpn_server, jury):
    logging.info(f"Writing inventory file to {ansible_path / 'inventory.ini'}")
    inventory_template = env.get_template(str(template_path / 'inventory.j2'))
    with open(ansible_path / 'inventory.ini', 'w') as file:
        file.write(inventory_template.render(
            teams=teams, vpn=vpn_server, jury=jury))


def get_public_ips(terraform_path, module_prefix):
    """
    Возвращает словарь {имя_ресурса: публичный_IP} для всех инстансов, чьи module начинается с module_prefix.
    Например: module_prefix = "module.vuln", "module.vpn", "module.jury"
    """
    tfstate_path = terraform_path / "terraform.tfstate"
    if not tfstate_path.exists():
        logging.critical(
            f"{tfstate_path} file not found - maybe you need to create resources in terraform/ad/ dir with command \"terraform apply\"")
        return {}

    logging.info(f"Reading terraform state from {tfstate_path}")
    with open(tfstate_path, "r") as file:
        tfstate = json.load(file)

        result = {}
        for resource in tfstate.get("resources", []):
            module = resource.get("module", "")
            if module.startswith(module_prefix) and resource.get("type") == "yandex_compute_instance":
                for instance in resource.get("instances", []):
                    attributes = instance.get("attributes", {})
                    interfaces = attributes.get("network_interface", [])
                    if interfaces:
                        ip = interfaces[0].get("nat_ip_address")
                        # Имя достаем из module, например module.vuln["team1"] -> team1
                        name = module.split(module_prefix)[-1].strip('["]')
                        if not name:  # Если модуль без for_each (например vpn или jury)
                            name = module_prefix.split('.')[-1]
                        result[name] = ip
        logging.info(f"Retrieved public IPs: {result}")
        return result


def generate_readme_files(env, template_path, teams):
    RESULT_PATH.mkdir(exist_ok=True)

    if not TOKENS_PATH.exists():
        logging.critical(
            "tokens.txt file not found - maybe Forcad not started yet")

    with open(TOKENS_PATH, "r") as file:
        tokens = {}
        for line in file:
            team, token = line.strip().split(':')
            tokens[team] = token

    for team in teams:
        team_dir = RESULT_PATH / team["id"]
        team_dir.mkdir(exist_ok=True)
        team["token"] = tokens[team["name"]]
        readme_template = env.get_template(
            str(template_path / 'readme.txt.j2'))
        with open(team_dir / 'readme.txt', 'w') as file:
            file.write(readme_template.render(team=team))

    logging.info(f"Generated readme.txt files in {RESULT_PATH}")


def archivate_team_dirs(teams):
    for team in teams:
        shutil.make_archive(RESULT_PATH / team["name"], 'zip', RESULT_PATH / team["id"])


@click.group()
def cli():
    pass


@cli.command(help="Generate ansible`s configs")
def generate_ansible():
    logging.info("Starting to generate Ansible configurations")

    config = load_config(CONFIG_PATH)
    env = setup_environment(BASE_PATH)

    teams = generate_team_data(config)
    
    vpn_server = config["cloud"]["vpn"]
    vpn_server["public_ip"] = get_public_ips(TERRAFORM_PATH, "module.vpn")["vpn"]
    
    jury = config["cloud"]["jury"]
    jury["public_ip"] = get_public_ips(TERRAFORM_PATH, "module.jury")["jury"]

    write_yaml_config(config, CONFIG_PATH)
    write_inventory_file(env, TEMPLATE_PATH, ANSIBLE_PATH,
                         teams, vpn_server, jury)


@cli.command(help="Generate terraform`s main.tf")
def generate_terraform():
    logging.info("Starting to generate Terraform configurations")

    config = load_config(CONFIG_PATH)
    env = setup_environment(BASE_PATH)

    teams = generate_team_data(config)
    cloud = config.get("cloud", {})
    logging.info(
        f"Writing Terraform main configuration to {TERRAFORM_PATH / 'main.tf'}")
    terraform_template = env.get_template(str(TEMPLATE_PATH / 'main.tf.j2'))
    with open(TERRAFORM_PATH / "main.tf", 'w') as file:
        file.write(terraform_template.render(
            teams=teams, cloud=cloud))


@cli.command(help="Generate result")
def generate_result():
    logging.info("Getting tokens for teams")
    run_command(["ansible-playbook", "grab-tokens.yml",],
                str(ANSIBLE_PATH.absolute()))

    logging.info("Generating result directory")
    config = load_config(CONFIG_PATH)
    env = setup_environment(BASE_PATH)
    teams = config.get("teams", [])
    generate_readme_files(env, TEMPLATE_PATH, teams)
    archivate_team_dirs(teams)


@cli.command(help="Create all VMs")
@click.pass_context
def create(ctx):
    ctx.invoke(generate_terraform)

    tfstate_path = TERRAFORM_PATH / "terraform.tfstate"
    if not tfstate_path.exists():
        run_command(["terraform", "init"],
                    str(TERRAFORM_PATH.absolute()))

    logging.info("Applying Terraform configurations")
    run_command(["terraform", "apply", "-auto-approve"],
                str(TERRAFORM_PATH.absolute()))

    ctx.invoke(generate_vpn)


@cli.command(help="Destroy all VMs")
def destroy():
    logging.info("Destroying all VMs")
    run_command(["terraform", "destroy", "-auto-approve"],
                str(TERRAFORM_PATH.absolute()))


@cli.command(help="Deploy VPN network")
def deploy_network():
    logging.info("Deploying VPN network")
    run_command(["ansible-playbook", "deploy-network.yml"],
                str(ANSIBLE_PATH.absolute()))


@cli.command(help="Generate VPN")
def generate_vpn():
    vpn_public_ip = get_public_ips(TERRAFORM_PATH, "module.vpn")["vpn"]
    if vpn_public_ip:
        config = load_config(CONFIG_PATH)
        teams = config.get("teams", [])
        logging.info("Generating VPN configurations")
        gen.run(range(1, len(teams) + 1), 20, vpn_public_ip)


@cli.command(help="Provision all VMs")
@click.pass_context
def provision(ctx):
    ctx.invoke(generate_ansible)
    logging.info("Applying Ansible configurations")
    run_command(["ansible-playbook", "deploy.yml"],
                str(ANSIBLE_PATH.absolute()))


@cli.command(help="Check avalability all VMs")
def ping():
    logging.info("Start ping all VMs")
    run_command(["ansible", "all", "-m", "ping"], str(ANSIBLE_PATH.absolute()))


@cli.command(help="Start services on vulnboxes")
def start_services():
    logging.info("Starting services")
    run_command(["ansible-playbook", "start-services.yml"],
                str(ANSIBLE_PATH.absolute()))


if __name__ == "__main__":
    cli()
