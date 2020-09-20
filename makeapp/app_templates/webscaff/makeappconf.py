import os
import shutil
from functools import partial

from makeapp.appconfig import Config, ConfigSetting
from makeapp.utils import temp_dir, replace_infile, run_command

join = os.path.join  # Short alias


class WebscaffConfig(Config):

    parent_template = ['pytest']

    domain = ConfigSetting(title='Domain Name', default='')
    email = ConfigSetting(title='Admin E-mail')
    host = ConfigSetting(title='Remote Host IP')

    def hook_rollout_init(self):
        super().hook_rollout_init()

        required = [
            'python3-dev',
            'python3-pip',
            'python3-venv',
            'python3-wheel',

            # For source builds.
            'build-essential',
            'libpcre3-dev', 'libssl-dev',  # for uWSGI with SSL and routing support

            'libpq-dev',
        ]

        self.print_banner(
            "You're about to rollout 'webscaff' skeleton.\n"
            f"Please make sure the following system packages are installed:\n  {' '.join(required)}")

    def hook_rollout_post(self):
        super().hook_rollout_post()

        module_name = self.app_template.maker.settings['module_name']
        self.module_name = module_name

        self.dir_project = os.getcwd()
        self.dir_package_root = join(self.dir_project, module_name)

        # Do things.
        self.prepare_venv()
        self.prepare_django_files()

        # Install into venv the package itself not to conflict
        # with Django's `startproject` command.
        run_command('. venv/bin/activate && pip install -e .')

        # Initialize local sqlite DB.
        run_command(f'venv/bin/{module_name} migrate')

    def prepare_venv(self):
        self.logger.info('Bootstrapping virtual environment for project ...')

        run_command('python3 -m venv venv/')

        cmd_install = '. venv/bin/activate && pip install -r '

        run_command(cmd_install + 'requirements.txt')
        run_command(cmd_install + 'tests/requirements.txt')

    def prepare_django_settings_base(self, dir_tmp):

        module_name = self.module_name

        source_file = join(dir_tmp, module_name, 'settings.py')

        replace_infile(
            source_file,
            pairs={
                # Add basic project-related settings.
                'from pathlib import Path':

                    'from pathlib import Path\n\n'
                    'from .sub_paths import *\n\n',

                #  Reset debug.
                'DEBUG = True':

                    'DEBUG = False',

                # Add core application.
                "    'django.contrib.staticfiles',":

                    "    'django.contrib.staticfiles',\n\n"
                    "    'uwsgiconf.contrib.django.uwsgify',\n\n"
                    "    '%(module)s.core',\n" % {'module': module_name},
            })

        shutil.move(source_file, join(self.dir_package_root, 'settings', 'base.py'))

    def prepare_django_files(self):
        self.logger.info('Bootstrapping Django project and basic application ...')

        dir_package = self.dir_package_root
        module_name = self.module_name

        command_django_admin = './venv/bin/django-admin'

        with temp_dir() as dir_tmp:
            run_command(f'{command_django_admin} startproject {module_name} {dir_tmp}')

            # We'd replace settings module paths.
            replace = partial(
                replace_infile,
                pairs={f'{module_name}.settings': f'{module_name}.settings.auto'})

            source_file = join(dir_tmp, 'manage.py')
            replace(source_file)
            shutil.move(source_file, join(dir_package, 'manage.py'))

            source_file = join(dir_tmp, module_name, 'wsgi.py')
            replace(source_file)
            shutil.move(source_file, join(dir_package, 'wsgi.py'))

            self.prepare_django_settings_base(dir_tmp)

            shutil.move(join(dir_tmp, module_name, 'urls.py'), join(dir_package, 'urls.py'))

        # Create basic app.
        dir_app = join(dir_package, 'core')
        run_command(f'{command_django_admin} startapp core {dir_app}')


makeapp_config = WebscaffConfig
