import os
import argparse
import click
from datetime import datetime

from sage_drop.client import Client
from sage_drop import cli as commands


locations = {
    'office': 0,
    'home': 1
}


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
                'Invalid date format. Please use YYYY-MM-DD.')


def get_client():
    try:
        user_name = os.environ['SAGE_USER']
        password = os.environ['SAGE_PASSWORD']
    except Exception:
        print('Missing environment variables SAGE_USER and SAGE_PASSWORD')

    return Client('http://sage.fabfab.de/', user_name, password)


@click.group()
def cli():
    pass


@cli.command(help="Show current balance")
def balance():
    commands.balance(get_client())


@cli.command(help="Clock in")
def come():
    commands.come(get_client(), False)


@cli.command(help="Clock out")
def go():
    commands.go(get_client(), False)


@cli.command('break', help="Clock out for a break")
def go_break():
    commands.go(get_client(), True)


@cli.command('return', help="Clock in")
def come_back():
    commands.come(get_client(), True)


@cli.command(help="List times")
@click.option("-f", "--from", "from_date",
              type=valid_date,
              help="Times from this date, or monday if empty")
@click.option("-t", "--to", "to_date",
              type=valid_date,
              help="Times to this date, or now if empty")
@click.option("-r", "--range", "range_days",
              type=int,
              help="Last X days")
def times(from_date, to_date, range_days):
    commands.times(get_client(), from_date, to_date, range_days)
