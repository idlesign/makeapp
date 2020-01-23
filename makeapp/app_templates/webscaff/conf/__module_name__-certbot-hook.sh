#! /bin/sh
chown -R {{ module_name }}:{{ module_name }} /etc/letsencrypt/archive/{{ webscaff_domain }}/.*
systemctl restart {{ module_name }}.service
