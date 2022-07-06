# Declarative `setuptools` Config Requirements Files Support

This projects adds the ability for projects using setuptools declarative configuration
to specify requirements using requirements files.

### ⚠ **There's a reason why this isn't, at least yet, supported by default. Please [read why](https://github.com/pypa/setuptools/issues/1951).**

Anyway, if you know what you're doing, then this library solves the missing feature
of defining requirements using requirements files.

## `setup.cfg`
Your `setup.cfg` should include a section named `requirements-files`, like:

```ini
[requirements-files]
setup_requires = requirements/setup.txt
install_requires = requirements/base.txt
tests_require = requirements/tests.txt
extras_require =
  docs = requirements/docs.txt
  cli = requirements/cli.txt
```

### ⚠ ATTENTION

#### The requirements files **MUST** be included in the wheel file aswell as the source tarball

For the example shown above, in ``setup.cfg``, add something like:

```ini
[options.data_files]
. = requirements/*.txt
```

Or something like the folowing on your ``MANIFEST.in``:

```
include requirements/*.txt
```

Or, if you use [setuptools-scm](https://pypi.org/project/setuptools-scm), the requirements files
need to be committed to the SCM repo.


## `pyproject.toml`
Your `pyproject.toml` should also include `setuptools-declarative-requirements`:
```toml
[build-system]
requires = ["setuptools>=50.3.2", "wheel", "setuptools-declarative-requirements"]
build-backend = "setuptools.build_meta"
```

## `setup.py`
Some projects still use a `setup.py` shim, similar to:
```python
#!/usr/bin/env python
import setuptools

if __name__ == "__main__":
    setuptools.setup()
```

If this is your case, your `setup.cfg` needs an extra bit of tweak. Make sure you have
``setuptools-declarative-requirements`` in your `setup_requires`:
```ini
[options]
setup_requires =
  setuptools>=50.3.2
  setuptools-declarative-requirements
```

## Do Note That
### ⚠ This project makes no attempt to validate your requirements files.
**The only thing it does is include every non empty line from your requirements files which does
not start with `#`, `-r` or `--`.**
