import os

BASE_DIR = os.path.dirname("./")
RESULT_DIR_CLIENT = os.path.join(BASE_DIR, 'ansible', 'roles', 'vpn-client', 'files', 'vpns')
RESULT_DIR_SERVER = os.path.join(BASE_DIR, 'ansible', 'roles', 'vpn-server', 'files', 'vpns')
TEMPLATES_PATH = os.path.join(BASE_DIR, 'templates')

TEAM_CLIENT_DIR = os.path.join(RESULT_DIR_CLIENT, 'team')
VULN_CLIENT_DIR = os.path.join(RESULT_DIR_CLIENT, 'vuln')
JURY_CLIENT_DIR = os.path.join(RESULT_DIR_CLIENT, 'jury')

TEAM_SERVER_DIR = os.path.join(RESULT_DIR_SERVER, 'team')
VULN_SERVER_DIR = os.path.join(RESULT_DIR_SERVER, 'vuln')
JURY_SERVER_DIR = os.path.join(RESULT_DIR_SERVER, 'jury')

TEAM_PORT = 30000
VULN_PORT = 31000
JURY_PORT = 32000
