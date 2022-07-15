import pathlib
import sys
from functools import wraps

from distutils import log


def _parse_requirements_file(requirements_file):
    if not requirements_file.is_file():
        log.error(
            "The requirements file '%s' does not exist",
            requirements_file,
        )
        sys.exit(1)
    parsed_requirements = []
    for line in requirements_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-i", "-r", "--")):
            continue
        parsed_requirements.append(line)
    log.info(
        "Requirements parsed from '%s': %s",
        requirements_file,
        ", ".join("'{}'".format(req) for req in parsed_requirements),
    )
    return parsed_requirements


def load_declarative_requirements_files(func, dist):
    """
    This function will return a wrapper arround ``dist.parse_config_files``
    in order for us to get the declarative requirements files, AFTER, the
    config files have been parsed
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Parse configuration files
        func(*args, **kwargs)
        # Load the declarative requirements files config
        requirements = dist.command_options.get("requirements-files")
        if not requirements:
            log.info("No 'requirements-files' section was found. Nothing to do.")
            return

        supported_config_keys = (
            "setup_requires",
            "install_requires",
            "extras_require",
            "tests_require",
        )

        for cfgname, (cfgfile, requirements_file) in requirements.items():
            if cfgfile != "setup.cfg":
                # We only support configuring requirements files in setup.cfg
                continue

            if cfgname not in supported_config_keys:
                log.error(
                    "The config key '%s' under 'requirements-files' is not "
                    "supported. Allowed config keys: %s",
                    cfgname,
                    ", ".join("'{}'".format(key) for key in supported_config_keys),
                )
                sys.exit(1)

            if cfgname == "extras_require":
                # Extras require supports mappings, let's parse that out
                if dist.extras_require is None:
                    # If dist.extras_require is still None, make it a dictionary
                    dist.extras_require = {}
                extras_require = dist.extras_require
                for line in requirements_file.splitlines():
                    if not line.strip():
                        # Ignore empty lines
                        continue
                    if "=" not in line:
                        log.error(
                            "Don't know how to parse the line '%s' for extras_require "
                            "under 'requirements-files'. Should be "
                            "'<extras_key> = path/to/requirements.txt'",
                            line.strip(),
                        )
                        sys.exit(1)
                    extras_key, extras_requirements_file = (
                        part.strip() for part in line.split("=")
                    )
                    if extras_key not in extras_require:
                        extras_require[extras_key] = []
                    extras_require[extras_key].extend(
                        _parse_requirements_file(pathlib.Path(extras_requirements_file))
                    )
                continue

            # The rest of the allowed config keys don't support mappings
            if getattr(dist, cfgname) is None:
                # If the dist value for the attribute is still None, make it a list
                setattr(dist, cfgname, [])
            getattr(dist, cfgname).extend(
                _parse_requirements_file(pathlib.Path(requirements_file.strip()))
            )

        # Be sure to call dist._finalize_requires again so that the distribution class
        # set's additional attributes
        dist._finalize_requires()

    return wrapper


def patch_parse_config_files(dist):
    """
    This function will only add a wrapper around ``dist.parse_config_files`` so
    that we can have setuptools/distutils do the config file parsing instead of
    us.
    """
    dist.parse_config_files = load_declarative_requirements_files(
        dist.parse_config_files, dist
    )


# Make our parse_requirements function the last to be evaluated
patch_parse_config_files.order = sys.maxsize
