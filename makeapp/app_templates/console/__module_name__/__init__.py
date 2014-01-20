import sys
import argparse

VERSION = (0, 1, 0)


def main():

    arg_parser = argparse.ArgumentParser(prog='{{ module_name }}', description='{{ description }}')

    arg_parser.add_argument('arg1', help='arg1 help')
    arg_parser.add_argument('--version', action='version', version='%s %s' % ('%(prog)s', '.'.join(map(str, VERSION))))

    parsed_args = arg_parser.parse_args()

    # Logic goes here.
    # if parsed_args.version:

    sys.exit(1)

