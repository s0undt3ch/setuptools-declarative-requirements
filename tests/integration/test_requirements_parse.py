import pytest


@pytest.fixture
def project(project, pypi_server_port):
    project.write_file(
        "requirements/setup.txt",
        contents="""
        -i http://localhost:{}

        setup-requires-pkg
        """.format(
            pypi_server_port
        ),
    )
    project.write_file(
        "requirements/base.txt",
        contents="""
        --index-url=http://localhost:{}

        install-requires-pkg
        """.format(
            pypi_server_port
        ),
    )
    project.write_file("requirements/docs.txt", contents="docs-extras-require-pkg")
    project.write_file("requirements/cli.txt", contents="cli-extras-require-pkg")
    project.write_file("requirements/tests.txt", contents="tests-require-pkg")
    project.create_pkg_tree(
        setup_requires="requirements/setup.txt",
        install_requires="requirements/base.txt",
        tests_require="requirements/tests.txt",
        extras_require={
            "docs": "requirements/docs.txt",
            "cli": "requirements/cli.txt",
        },
    )
    yield project


@pytest.mark.parametrize("build", ["sdist", "bdist_wheel"])
def test_build_package(project, build):
    ret = project.sys_exec_run("setup.py", build)
    assert ret.returncode == 0
    package = project.get_generated_dist()
    with project.virtualenv() as venv:
        installed_packages = venv.get_installed_packages()
        assert "install-requires-pkg" not in installed_packages
        ret = venv.install(str(package))
        assert ret.returncode == 0, ret
        installed_packages = venv.get_installed_packages()
        assert "install-requires-pkg" in installed_packages

        # Now the docs extras
        installed_packages = venv.get_installed_packages()
        assert "docs-extras-require-pkg" not in installed_packages
        ret = venv.install("{}[docs]".format(package))
        assert ret.returncode == 0, ret
        installed_packages = venv.get_installed_packages()
        assert "docs-extras-require-pkg" in installed_packages

        # Now the cli extras
        installed_packages = venv.get_installed_packages()
        assert "cli-extras-require-pkg" not in installed_packages
        ret = venv.install("{}[cli]".format(package))
        installed_packages = venv.get_installed_packages()
        assert ret.returncode == 0, ret
        assert "cli-extras-require-pkg" in installed_packages
