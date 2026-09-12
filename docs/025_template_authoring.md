# Template authoring

A template is a directory whose files are rendered with Jinja and copied into the generated project. Named user
templates live under `~/.makeapp/app_templates/`; a template directory path can also be passed directly to `-t`.

!!! warning
    If a template contains `makeappconf.py`, makeapp imports and executes it as Python. Treat templates like source code
    and use only trusted templates.

## Minimal template

Create a named template:

```text
~/.makeapp/app_templates/cool/
├── README.md
└── src/
    └── __package_name__/
        └── cool.py
```

Use built-in settings in file contents:

```markdown title="README.md"
# {{ app_name }}

{{ description }}
```

The `__package_name__` directory marker is replaced with the resolved import package name. For example, the
application name `acme_tool` produces `src/acme_tool/cool.py`.

Roll out the template by name:

```bash
ma new acme_tool ./acme-tool -t cool --no-prompt
```

Or pass its path:

```bash
ma new acme_tool ./acme-tool -t ./templates/cool --no-prompt
```

## Settings

Add `makeappconf.py` to declare settings:

```python title="makeappconf.py"
from makeapp.appconfig import Config, ConfigSetting


class CoolConfig(Config):
    color = ConfigSetting(title='Primary color', default='blue')


makeapp_config = CoolConfig
```

The setting becomes `cool_color`, combining the template directory name and attribute name. Reference it from files as
`{{ cool_color }}` and provide it non-interactively as:

```bash
ma new acme_tool ./acme-tool -t cool --no-prompt --cool_color green
```

`ConfigSetting` accepts a prompt title, a default value, and an optional Click-compatible `type`. If no current value is
available, makeapp asks for it while configuring the rollout.

## Template inheritance

A configuration class may inject parent templates:

```python title="makeappconf.py"
from makeapp.appconfig import Config


class CoolConfig(Config):
    parent_template = ['console']


makeapp_config = CoolConfig
```

For a file that exists in a parent template, start the child file with Jinja inheritance and override named blocks:

```jinja
{% extends parent_template %}
{% block deps %}
{{ super() }}
    "rich",
{% endblock %}
```

`parent_template` is resolved dynamically for the same relative file path. Built-in templates demonstrate reusable
blocks in `pyproject.toml` and command-line modules.

When several templates contribute the same path, the later template controls the rendered destination. Use
`{{ super() }}` in an inherited block when parent content must be preserved.

## Rollout hooks

Override hooks on the configuration class to perform work around rendering:

```python title="makeappconf.py"
from makeapp.appconfig import Config


class CoolConfig(Config):
    def hook_rollout_pre(self):
        self.logger.info('Preparing the rollout')

    def hook_rollout_post(self):
        super().hook_rollout_post()
        self.logger.info('Rollout complete')


makeapp_config = CoolConfig
```

Available hooks are:

| Hook | Timing |
| --- | --- |
| `hook_rollout_init` | After templates and the renderer are initialized. |
| `hook_configure` | While missing template settings are collected. |
| `hook_rollout_pre` | In the destination directory before files are rendered. |
| `hook_rollout_post` | In the destination directory after files are rendered. |

The base `hook_rollout_post` implements cleanup. Call `super()` when overriding it.

## Cleanup

Set `cleanup` to remove paths after all files have been rendered:

```python
class CoolConfig(Config):
    cleanup = ['tests']
```

Cleanup paths are resolved relative to the generated project. Use it when a specialized template intentionally removes
content contributed by the default or parent template.

## File conflicts and permissions

- Template files replace earlier template contributions with the same relative path.
- Existing files in the destination are preserved unless `ma new --overwrite_on_conflict` is used.
- Source file permissions are copied to generated files.
- `makeappconf.py`, bytecode, and cache files are not copied into the destination.
