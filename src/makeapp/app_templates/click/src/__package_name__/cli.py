{% extends parent_template %}


{% block imports %}
import sys
import click
from {{ package_name }} import VERSION
{% endblock %}


{% block body %}
@click.group()
@click.version_option(version=VERSION)
def entry_point():
    """{{ package_name }} command line utilities."""


@entry_point.command()
@click.argument('arg')
@click.option('--opt', help='opt help', type=click.Choice([1, 2, 3]))
def command(arg, opt):
    """Some command"""
    click.secho('Not implemented', fg='red', err=True)
    sys.exit(1)


def main():
    entry_point(obj={})

{% endblock %}
