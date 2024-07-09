#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import pathlib
import subprocess

import pytest
import yaml

ROCK_EXPECTED_FILES = [
    "/install-cni.sh",
    "/ip-control-loop",
    "/whereabouts",
]

METADATA = yaml.safe_load(pathlib.Path("./rockcraft.yaml").read_text())
# Assuming rock name is the same as application name.
ROCK_NAME = METADATA["name"]
VERSION = METADATA["version"]
LOCAL_ROCK_IMAGE = f"{ROCK_NAME}:{VERSION}"


def _run_in_docker(check_exit_code, *command):
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-i",
            LOCAL_ROCK_IMAGE,
            "exec",
            *command,
        ],
        check=check_exit_code,
        capture_output=True,
        text=True,
    )


@pytest.mark.abort_on_fail
def test_whereabouts_rock():
    """Test Whereabouts rock."""
    # check rock filesystem
    _run_in_docker(True, "ls", "-la", *ROCK_EXPECTED_FILES)

    # check binary name and version.
    process = _run_in_docker(True, f"/{ROCK_NAME}", "version")
    output = process.stderr
    assert ROCK_NAME in output and VERSION in output

    # check other binary. It expects KUBERNETES_SERVICE_HOST to be defined.
    process = _run_in_docker(False, "/ip-control-loop")
    assert "KUBERNETES_SERVICE_HOST" in process.stderr

    # check script. It expects serviceaccount token to exist.
    process = _run_in_docker(False, "/install-cni.sh")
    expected_error = (
        "cat: /var/run/secrets/kubernetes.io/serviceaccount/token: "
        "No such file or directory"
    )
    assert expected_error == process.stderr.strip()
