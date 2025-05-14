from uwsgiconf.runtime.scheduling import register_cron, register_timer
from uwsgiconf.runtime.mules import Farm
from uwsgiconf.runtime.spooler import Spooler

# Put uWSGI related configuration here and it'll be loaded
# in uWSGI master process on startup.

# spooler = Spooler.get_by_basename('spool')
# farms = Farm.get_farms()
