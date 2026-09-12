# Configuration

User configuration is stored in `makeapp.conf` under the `.makeapp` directory in the user's home directory.

=== "Linux and macOS"

    ```text
    ~/.makeapp/makeapp.conf
    ```

=== "Windows"

    ```text
    %USERPROFILE%\.makeapp\makeapp.conf
    ```

## Setting precedence

Settings are applied from the lowest to the highest priority:

1. built-in defaults;
2. `~/.makeapp/makeapp.conf`;
3. the file passed with `ma new --configuration_file`;
4. command-line options and custom `--name value` arguments;
5. values requested interactively by template configuration.

## Configuration file

The file uses INI syntax and requires a `[settings]` section:

```ini title="makeapp.conf"
[settings]
author = The Librarian
author_email = librarian@example.com
license = bsd3cl
url = https://github.com/librarian/{{ app_name }}
vcs = git
year = 2026
```

Standard settings are:

| Setting | Purpose | Default |
| --- | --- | --- |
| `app_name` | Distribution name passed to `ma new` | Required argument |
| `package_name` | Import package name | Segment after the first `-`, with `-` changed to `_` |
| `description` | Short package description | `Sample short description` |
| `author` | Author name | `<app_name> contributors` |
| `author_email` | Author email | Empty |
| `url` | Project homepage | Project page on PyPI |
| `year` | Copyright year | Current year |
| `license` | License template alias | `bsd3cl` |
| `vcs` | Version control system | `git` |
| `vcs_remote` | Remote repository URL | Empty |
| `python_version` | Minimum generated Python version | Current major/minor version |

Supported license aliases are `no`, `mit`, `apache2`, `gpl2`, `gpl3`, `bsd2cl`, and `bsd3cl`.

Values may contain markers such as `{{ app_name }}`. Markers referring to settings already resolved by `makeapp` are
replaced before rendering the templates.

Use another configuration file for a single rollout:

```bash
ma new app ./app --configuration_file ./team-makeapp.conf
```

## Template-specific settings

Templates can declare additional settings. Pass them as `--name value` pairs after the standard options:

```bash
ma new website ./website -t webscaff --no-prompt \
  --webscaff_domain example.com \
  --webscaff_email admin@example.com \
  --webscaff_host 203.0.113.10
```

Unknown custom arguments must always be passed in pairs. When using `--no-prompt`, provide every required
template-specific setting to avoid an interactive prompt.

## User template directory

Named user templates are discovered under:

```text
~/.makeapp/app_templates/<template-name>/
```

For example:

```bash
mkdir -p ~/.makeapp/app_templates/cool
printf '%s\n' "You'd better be cool." > ~/.makeapp/app_templates/cool/COOL.txt
ma new app ./app -d "My application" -t cool
```

The default scaffold is always applied first. Files from `cool` then extend or override it. A comma-separated list
applies several templates in the specified order.

```bash
ma new app ./app -t console,cool
```

!!! warning
    A template can contain `makeappconf.py`, which is imported and executed as Python code. Only use templates from
    sources you trust.

See [Template authoring](025_template_authoring.md) for configuration classes, inheritance, hooks, and cleanup.
