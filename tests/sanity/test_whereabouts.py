#
# Copyright 2024 Canonical, Ltd.
#
import os
import subprocess

import pytest

ROCK_EXPECTED_FILES = [
    "/install-cni.sh",
    "/ip-control-loop",
    "/whereabouts",
]


def _run_in_docker(image, check_exit_code, *command):
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-i",
            image,
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
    image_variable = "ROCK_WHEREABOUTS"
    image = os.getenv(image_variable)
    assert image is not None, f"${image_variable} is not set"
    # check rock filesystem
    _run_in_docker(image, True, "ls", "-la", *ROCK_EXPECTED_FILES)

    # check binary name and version.
    process = _run_in_docker(image, True, "/whereabouts", "version")
    output = process.stderr
    assert "whereabouts" in output and "0.6.3" in output

    # check other binary. It expects KUBERNETES_SERVICE_HOST to be defined.
    process = _run_in_docker(image, False, "/ip-control-loop")
    assert "KUBERNETES_SERVICE_HOST" in process.stderr

    # check script. It expects serviceaccount token to exist.
    process = _run_in_docker(image, False, "/install-cni.sh")
    "cat: /var/run/secrets/kubernetes.io/serviceaccount/token: No such file or directory" in process.stderr
