# Developer tools

Makeapp gives you some tools to further facilitate the development process.

## Bootstrap virtual environment

When you've got an app sources and want to initialize the environment to develop the app 
use `up` command (inside the directory with `pyproject.toml`).

```bash
ma up
```

## Register the CLI application as a tool

If your application has a CLI (e.g. exposes `project.scripts`) you can register
it as a tool. So that the command issued in terminal will invoke just the code you develop.

```bash
ma up -t
# or ma up --tool
```

## Regenerate the environment

Sometimes something may go wrong with the virtual environment so that you may want 
to drop the old one altogether and create a new one. Use the following command: 

```bash
ma up -r
# or ma up --reset
```

## Style code

To style/lint your code use the following command: 

```bash
ma style
```
