import pytest


@pytest.fixture
def project(project):
    project.write_file("requirements/base.txt", contents="pep8")
    project.write_file("requirements/docs.txt", contents="sphinx")
    project.write_file("requirements/tests.txt", contents="pytest")
    project.create_pkg_tree(
        install_requires="requirements/base.txt",
        extras_require={
            "docs": "requirements/docs.txt",
            "tests": "requirements/tests.txt",
        },
    )
    yield project


@pytest.mark.parametrize("build", ["sdist", "bdist_wheel"])
def test_build_package(project, build):
    ret = project.sys_exec_run("setup.py", build)
    assert ret.exitcode == 0
    package = project.get_generated_dist()
    with project.virtualenv() as venv:
        assert "pep8" not in venv.get_installed_packages()
        venv.install(str(package))
        assert "pep8" in venv.get_installed_packages()

        # Now the tests extras
        assert "pytest" not in venv.get_installed_packages()
        venv.install(f"{package}[tests]")
        assert "pytest" in venv.get_installed_packages()

        # Now the docs extras
        assert "sphinx" not in venv.get_installed_packages()
        venv.install(f"{package}[docs]")
        assert "sphinx" in venv.get_installed_packages()
