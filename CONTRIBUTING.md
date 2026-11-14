# makeapp contributing


## Submit issues

If you spotted something weird in application behavior or want to propose a feature you are welcome.


## Write code

If you are eager to participate in application development and to work on an existing issue (whether it should
be a bugfix or a feature implementation), fork, write code, and make a pull request right from the forked project page.

When contributing code, follow the rules from [IDLE.md](https://github.com/idlesign/makeapp/blob/master/IDLE.md).


## Project workflow

```bash
ma up              # Synchronize the development environment.
ma style           # Run Ruff checks and apply safe fixes.
ma tests           # Run the configured test matrix.
ma docs --build    # Build documentation without starting a server.
ma change "+ Add a feature"  # Update the changelog and commit modified files.
ma release         # Prepare a release and optionally publish it.
```

Review changes before running `ma change`: it stages and commits modified tracked files together with the changelog.


## Spread the word

If you have some tips and tricks or any other words that you think might be of interest for the others — publish it
wherever you find convenient.


See also: <https://github.com/idlesign/makeapp>
