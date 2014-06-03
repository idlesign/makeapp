import sys
import argparse

VERSION = (0, 1, 0)


def main():

    arg_parser = argparse.ArgumentParser(prog='{{ module_name }}', description='{{ description }}', version='.'.join(map(str, VERSION)))

    arg_parser.add_argument('arg1', help='arg1 help')
    arg_parser.add_argument('--opt', help='optional arg help', action='store_true')

    parsed_args = arg_parser.parse_args()
    # parsed_args = vars(parsed_args)  # Convert args to dict

    # Logic goes here.
    # if parsed_args['opt']:

    sys.exit(1)

