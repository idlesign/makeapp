from __future__ import absolute_import
import os
import shutil
from functools import partial

from makeapp.appconfig import Config, ConfigSetting, temp_dir, replace_infile, check_command, run_command


join = os.path.join  # Short alias


class WebscaffConfig(Config):

    command_venv = 'virtualenv'

    parent_template = ['pytest']

    host = ConfigSetting(title='Remote host')

    def hook_rollout_pre(self):
        super(WebscaffConfig, self).hook_rollout_pre()

        check_command(self.command_venv, 'virtual environment creation script')

    def hook_rollout_post(self):
        super(WebscaffConfig, self).hook_rollout_post()

        module_name = self.app_template.maker.settings['module_name']
        self.module_name = module_name

        self.dir_project = os.getcwd()
        self.dir_package_root = join(self.dir_project, module_name)
        self.dir_package = join(self.dir_package_root, module_name)

        # Do things.
        self.reorganize_package_dir()
        self.prepare_venv()
        self.prepare_django_files()

        # Install into venv the package itself as last step so to not conflict
        # with Django's `startproject` command.
        run_command('. venv/bin/activate && pip install -e %s/' % self.module_name)

    def reorganize_package_dir(self):
        """Moves a package directory into the same named subdirectory."""
        self.logger.info('Building webscaff project directory ...')

        with temp_dir() as dir_tmp:
            run_command('mv * %(tmp)s && mv %(tmp)s %(inner)s' % {'tmp': dir_tmp, 'inner': self.module_name})

        # Moving items into project root.
        def move_up(name):
            shutil.move(join(self.dir_package_root, name), self.dir_project)

        move_up('conf')
        move_up('dump')
        move_up('wscaff.yml')

    def prepare_venv(self):
        self.logger.info('Bootstrapping virtual environment for project ...')

        run_command('%s -p python3 venv/' % self.command_venv)
        run_command('. venv/bin/activate && pip install -r %s/requirements.txt' % self.module_name)

    def prepare_django_files(self):
        self.logger.info('Bootstrapping Django project and basic application ...')

        dir_package = self.dir_package
        module_name = self.module_name

        command_django_admin = './venv/bin/django-admin'

        with temp_dir() as dir_tmp:
            run_command('%s startproject %s %s' % (command_django_admin, module_name, dir_tmp))

            # We'd replace settings module paths.
            replace = partial(
                replace_infile,
                pairs=(('%s.settings' % module_name, '%s.settings.settings' % module_name),))

            source_file = join(dir_tmp, 'manage.py')
            replace(source_file)
            shutil.move(source_file, join(dir_package, 'manage.py'))

            source_file = join(dir_tmp, module_name, 'wsgi.py')
            replace(source_file)
            shutil.move(source_file, join(dir_package, 'wsgi.py'))

            source_file = join(dir_tmp, module_name, 'settings.py')
            replace_infile(
                source_file,
                pairs=(
                    ('DEBUG = True', 'DEBUG = False'),
                    # Add core application.
                    ("    'django.contrib.staticfiles',",
                     "    'django.contrib.staticfiles',\n\n"
                     "    'uwsgiconf.contrib.django.uwsgify',\n\n"
                     "    '%(module)s.core',\n" % {'module': module_name}),
                ))
            shutil.move(source_file, join(dir_package, 'settings', 'settings_base.py'))

            shutil.move(join(dir_tmp, module_name, 'urls.py'), join(dir_package, 'urls.py'))

        # Create basic app.
        dir_app = join(dir_package, 'core')
        os.mkdir(dir_app)
        run_command('%s startapp core %s' % (command_django_admin, dir_app))


makeapp_config = WebscaffConfig
