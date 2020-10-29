# Declarative `setuptools` Config Requirements Files Support

This projects adds the ability for projects using setuptools declarative configuration
to specify requirements using requirements files.

### ⚠ **There's a reason why this isn't, at least yet, supported by default. Please [read why](https://github.com/pypa/setuptools/issues/1951).**

Anyway, if you know what you're doing, then this library solves the missing feature of defining requirements using requirements files.

## Setup
Your `setup.cfg` should include a section named `requirements-files` like:

```ini
[requirements-files]
setup_requires = requirements/setup.txt
install_requires = requirements/base.txt
tests_require = requirements/tests.txt
extras_require =
  docs = requirements/docs.txt
  cli = requirements/cli.txt
```

### ⚠ This project makes no attempt to validate your requirements files.
**The only thing it does is include every non empty line from your requirements files which doesn't start with `#`, `-r` or `--`.**
