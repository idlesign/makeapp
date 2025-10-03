# Quickstart

## Before start

Makeapp may install basic development tools (`uv`, `ruff`) for you:

```bash
ma tools

; Upgrade with
ma tools -u
```

## Application scaffolding

Scaffold a new application:

```bash
ma new shiny_app /home/librarian/shiny/ --description "My app." --author "I am"
```

!!! note
    `ma` is a convenient alias for `makeapp` command.

This will create a decent application skeleton (`pyproject.toml`, docs, tests, etc.) and initialize Git repository.

Get some help on command line switches:

```bash
ma --help
```

### Settings in config

Put some default settings into a config (not to mess with command line switches anymore):

1. Create `.makeapp` (dot is required) directory in your HOME directory;
2. In `.makeapp` directory create `makeapp.conf` configuration file with a similar contents:

    ```ini
    [settings]
    author = The Librarian
    author_email = librarian@discworld.wrld
    license = bsd3cl
    url = https://github.discworld.wrld/librarian/{{ app_name }}
    vcs = git
    ```

### Settings in command line

You can also pass settings values via command line options. Use `--no-prompt` switch to automate scaffolding:

```bash
ma new tiny_app -t webscaff --no-prompt --webscaff_domain "example.com" --webscaff_email "me@example.com" --webscaff_host "93.184.216.34" --vcs_remote "git@example.com:me/my_new_app.git"
```

## Adding changes

When you're ready to add another entry to your changelog use `change` command 
(project directory containing `pyproject.toml`):

```bash
ma change "+ New 'change' command implemented"
```

This will also stage and commit all changed files.

Supported message prefixes and corresponding version number parts incremented 
on `release` command:

| symbol | meaning                          | version part increment |
|--------|----------------------------------|------------------------|
| `+`    | New feature / addition           | minor                  |
| `!`    | Important change/improvement/fix | patch                  |
| `-`    | Feature deprecation / removal    | patch                  |
| `*`    | Minor change/improvement/fix     | patch                  |


!!! note
    `*` prefix is added by default if none of the above-mentioned prefixes found.


## Application publishing

When you're ready to publish issue the following command
(project directory containing `pyproject.toml`):

```bash
ma release
; Bump version number part manually: major, minor, patch
ma release --increment major
; or 
ma release -i major
```

This will automatically:

  * bump up application version number
  * tag version in VCS
  * push sources to remote repository
  * upload application package to PyPI


## Bash completion

To enable bash completion for `ma` (or `makeapp`) command append the following line into your ``.bashrc``:

``` bash
eval "$(_MAKEAPP_COMPLETE=source makeapp)"
```
