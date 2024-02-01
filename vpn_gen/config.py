import os

BASE_DIR = os.path.dirname("./")
RESULT_DIR = os.path.join(BASE_DIR, 'ansible')
TEMPLATES_PATH = os.path.join(BASE_DIR, 'templates')

SERVER_CONFIG_DIR = os.path.join(RESULT_DIR, 'server')
TEAM_CLIENT_DIR = os.path.join(RESULT_DIR, 'team')
VULN_CLIENT_DIR = os.path.join(RESULT_DIR, 'vuln')
JURY_CLIENT_DIR = os.path.join(RESULT_DIR, 'jury')

TEAM_SERVER_DIR = os.path.join(SERVER_CONFIG_DIR, 'team')
VULN_SERVER_DIR = os.path.join(SERVER_CONFIG_DIR, 'vuln')
JURY_SERVER_DIR = os.path.join(SERVER_CONFIG_DIR, 'jury')

TEAM_PORT = 30000
VULN_PORT = 31000
JURY_PORT = 32000
