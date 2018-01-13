#!/usr/bin/env python

{% block imports %}
import sys
import argparse
from {{ module_name }} import VERSION_STR
{% endblock %}


{% block body %}
def main():

    arg_parser = argparse.ArgumentParser(prog='{{ module_name }}', description='{{ description }}')
    arg_parser.add_argument('--version', action='version', version=VERSION_STR)

    arg_parser.add_argument('arg1', help='arg1 help')
    arg_parser.add_argument('--opt', help='optional arg help', action='store_true', default=False)

    # subparsers = arg_parser.add_subparsers(dest='my_subparsers')
    # subcommand_parser = subparsers.add_parser('subcommand', help='subcommand help')

    parsed_args = arg_parser.parse_args()
    # parsed_args = vars(parsed_args)  # Convert args to dict
    # subparsed_args = parsed_args['subparsers']

    # Logic goes here.
    # if parsed_args['opt']:

    sys.exit(1)
{% endblock %}

if __name__ == '__main__':
    main()
