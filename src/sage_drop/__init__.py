import os
import argparse
from datetime import datetime

from sage_drop.client import Client
from sage_drop import cli as commands


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
                'Invalid date format. Please use YYYY-MM-DD.')


def cli():
    try:
        user_name = os.environ['SAGE_USER']
        password = os.environ['SAGE_PASSWORD']
    except Exception:
        print('Missing environment variables SAGE_USER and SAGE_PASSWORD')
        return

    parser = argparse.ArgumentParser(
            prog='sage',
            description='Because sage sucks'
            )
    subparsers = parser.add_subparsers(
            dest='command',
            title='commands',
            )
    subparsers.add_parser('come', help='Clock in')
    subparsers.add_parser('go', help='Clock out')
    subparsers.add_parser('break', help='Clock out for a break')
    subparsers.add_parser('balance', help='Show current balance')
    times_parser = subparsers.add_parser(
            'times',
            help='Show times'
            )
    times_parser.add_argument('from', nargs='?', type=valid_date,
                              help='From date')
    times_parser.add_argument('to', nargs='?', type=valid_date,
                              help='To date')
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
    client = Client('http://sage.fabfab.de/', user_name, password)
    if args.command == 'balance':
        commands.balance(client)
    elif args.command == 'come':
        commands.come(client)
    elif args.command == 'go':
        commands.go(client, False)
    elif args.command == 'break':
        commands.go(client, True)
    elif args.command == 'times':
        commands.times(client, getattr(args, 'from'), args.to)
