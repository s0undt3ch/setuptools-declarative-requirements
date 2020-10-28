import os
import pathlib
import sys
from distutils import log


def _parse_requirements_file(requirements_file):
    if not requirements_file.is_file():
        log.error(
            "The requirements file %s does not exist",
            requirements_file.relative_to(os.getcwd()),
        )
    parsed_requirements = []
    for line in requirements_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-r", "--")):
            continue
        parsed_requirements.append(line)
    log.info(
        "Requirements parsed from '%s': %s",
        requirements_file.relative_to(os.getcwd()),
        ", ".join(f"'{req}'" for req in parsed_requirements),
    )
    return parsed_requirements


def parse_requirements(dist):
    project_root = pathlib.Path(os.getcwd())
    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        log.warn("Could not find a pyproject.toml file")
        return
    defn = __import__("toml").load(pyproject)
    requirements = defn.get("requirements")
    if not requirements:
        log.warn("No 'requirements' section was found in 'pyproject.toml'")
        return
    for key, value in requirements.items():
        cvalue = getattr(dist, key)
        if isinstance(value, str):
            if cvalue is None:
                setattr(dist, key, [])
            getattr(dist, key).extend(_parse_requirements_file(project_root / value))
            continue
        if cvalue is None:
            setattr(dist, key, {})
        data = getattr(dist, key)
        for dkey, dvalue in value.items():
            if dkey not in data:
                data[dkey] = []
            data[dkey].extend(_parse_requirements_file(project_root / dvalue))


parse_requirements.order = sys.maxsize
