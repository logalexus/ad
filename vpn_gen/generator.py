import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

import config
import crypto_utils


class ConfigGenerator:
    def __init__(self, vpn_server, cn):
        self.jenv = Environment(
            loader=FileSystemLoader(config.TEMPLATES_PATH),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.cn = cn
        self.vpn_server = vpn_server
        self.ca_cert, self.ca_key = crypto_utils.create_ca(CN=cn)
        self.dhparam = crypto_utils.get_dhparam()

    @property
    def ca_cert_dump(self):
        return crypto_utils.dump_file_in_mem(self.ca_cert).decode()

    def get_template(self, name):
        return self.jenv.get_template(name)

    def _get_rendered(self, template, client_name, is_server, team_num, static_key):
        cert, key = None, None
        if client_name:
            cert, key = crypto_utils.generate_subnet_certs(
                ca_cert=self.ca_cert,
                ca_key=self.ca_key,
                client_name=client_name,
                serial=0x0C,
                is_server=is_server,
            )

        template = self.get_template(template)
        rendered = template.render(
            config=config,
            server_host=self.vpn_server,
            team_num=team_num,
            ca_cert=self.ca_cert_dump,
            cert=cert,
            key=key,
            static_key=static_key,
            dhparam=self.dhparam,
        )

        return rendered

    @staticmethod
    def _dump_file(rendered, filename):
        with open(filename, 'w') as f:
            f.write(rendered)

    @staticmethod
    def format_team_num(team_num):
        return str(team_num)

    def _generate_team(self, team_num, per_team):
        static_key = crypto_utils.generate_static_key()
        formatted_team = self.format_team_num(team_num)

        team_client_dir = os.path.join(config.TEAM_CLIENT_DIR, f'team{formatted_team}')
        os.makedirs(team_client_dir, exist_ok=True)

        for player_num in range(1, per_team + 1):
            client_name = f'team{formatted_team}_{player_num}'
            rendered = self._get_rendered(
                template='team_client.j2',
                client_name=client_name,
                is_server=False,
                team_num=team_num,
                static_key=static_key,
            )
            ovpn_dump_path = os.path.join(team_client_dir, f'{client_name}.ovpn')
            self._dump_file(rendered, ovpn_dump_path)

        server_name = f'team_server{formatted_team}'
        rendered = self._get_rendered(
            template='team_server.j2',
            client_name=server_name,
            is_server=True,
            team_num=team_num,
            static_key=static_key,
        )
        conf_dump_path = os.path.join(config.TEAM_SERVER_DIR, f'{server_name}.conf')
        self._dump_file(rendered, conf_dump_path)

    def _generate_vuln(self, team_num):
        formatted_team = self.format_team_num(team_num)
        static_key = crypto_utils.generate_static_key()
        rendered = self._get_rendered(
            template='vuln_client.j2',
            client_name=None,
            is_server=False,
            team_num=team_num,
            static_key=static_key,
        )
        ovpn_dump_path = os.path.join(config.VULN_CLIENT_DIR, f'team{formatted_team}.ovpn')
        self._dump_file(rendered, ovpn_dump_path)

        rendered = self._get_rendered(
            template='vuln_server.j2',
            client_name=None,
            is_server=True,
            team_num=team_num,
            static_key=static_key,
        )
        conf_dump_path = os.path.join(config.VULN_SERVER_DIR, f'vuln_server{formatted_team}.conf')
        self._dump_file(rendered, conf_dump_path)

    def generate_for_teams(self, team_list, per_team):
        for team_num in team_list:
            self._generate_team(team_num, per_team)

    def generate_for_vulns(self, team_list):
        for team_num in team_list:
            self._generate_vuln(team_num)

    def generate_for_jury(self):
        static_key = crypto_utils.generate_static_key()
        rendered = self._get_rendered(
            template='jury_client.j2',
            client_name=None,
            is_server=False,
            team_num=None,
            static_key=static_key,
        )
        ovpn_dump_path = os.path.join(config.JURY_CLIENT_DIR, 'jury.ovpn')
        self._dump_file(rendered, ovpn_dump_path)

        rendered = self._get_rendered(
            template='jury_server.j2',
            client_name=None,
            is_server=True,
            team_num=None,
            static_key=static_key,
        )
        conf_dump_path = os.path.join(config.JURY_SERVER_DIR, 'jury.conf')
        self._dump_file(rendered, conf_dump_path)
