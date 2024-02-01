#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import generator

sys.path = sys.path[1:]


def initialize():
    if os.path.exists(config.RESULT_DIR):
        shutil.rmtree(config.RESULT_DIR)

    os.makedirs(config.TEAM_SERVER_DIR, exist_ok=True)
    os.makedirs(config.VULN_SERVER_DIR, exist_ok=True)
    os.makedirs(config.JURY_SERVER_DIR, exist_ok=True)

    os.makedirs(config.TEAM_CLIENT_DIR, exist_ok=True)
    os.makedirs(config.VULN_CLIENT_DIR, exist_ok=True)
    os.makedirs(config.JURY_CLIENT_DIR, exist_ok=True)


def run(team_list, per_team, vpn_server, gen_team=True, gen_jury=True, gen_vuln=True):
    initialize()

    cg = generator.ConfigGenerator(vpn_server=vpn_server, cn='cbsctf.live')

    if gen_team:
        cg.generate_for_teams(team_list=team_list, per_team=per_team)

    if gen_vuln:
        cg.generate_for_vulns(team_list)

    if gen_jury:
        cg.generate_for_jury()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate openvpn configuration for AD CTFs')
    parser.add_argument('--server', '-s', type=str, help='Openvpn server host', required=True)
    parser.add_argument('--per-team', type=int, default=2, metavar='N', help='Number of configs per team')
    parser.add_argument('--team', help='Generate config for teams', action='store_true')
    parser.add_argument('--jury', help='Generate config for jury', action='store_true')
    parser.add_argument('--vuln', help='Generate config for vulnboxes', action='store_true')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--teams', '-t', type=int, metavar='N', help='Team count')
    group.add_argument('--range', type=str, metavar='N-N', help='Range of teams (inclusive)')
    group.add_argument('--list', type=str, metavar='N,N,...', help='List of teams')

    args = parser.parse_args()

    teams = None
    if args.team or args.vuln:
        if args.teams:
            teams = range(1, args.teams + 1)
        elif args.range:
            match = re.search(r"(\d+)-(\d+)", args.range)
            if not match:
                print('Invalid range')
                exit(1)

            teams = range(int(match.group(1)), int(match.group(2)) + 1)
        else:
            teams = list(map(int, args.list.split(',')))

    run(team_list=teams, per_team=args.per_team, vpn_server=args.server, gen_team=args.team, gen_jury=args.jury,
        gen_vuln=args.vuln)

    print(f"Done generating config for {len(teams or [])} teams")
