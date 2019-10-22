#! /bin/sh
chown -R {{ module_name }}:{{ module_name }} /etc/letsencrypt/archive/{{ webscaff_domain }}/.*
{{ module_name }} uwsgi_reload
