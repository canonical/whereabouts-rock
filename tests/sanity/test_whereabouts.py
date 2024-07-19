#
# Copyright 2024 Canonical, Ltd.
#
import os

import pytest
from k8s_test_harness.util import docker_util

ROCK_EXPECTED_FILES = [
    "/host",
    "/install-cni.sh",
    "/ip-control-loop",
    "/whereabouts",
]


def _test_whereabouts_rock(image_variable, expected_files):
    """Test Whereabouts rock."""
    image = os.getenv(image_variable)
    assert image is not None, f"${image_variable} is not set"

    # check rock filesystem
    docker_util.ensure_image_contains_paths(image, expected_files)

    # check binary name and version.
    version = docker_util.get_image_version(image)
    process = docker_util.run_in_docker(image, True, "/whereabouts", "version")
    output = process.stderr
    assert "whereabouts" in output and version in output

    # check other binary. It expects KUBERNETES_SERVICE_HOST to be defined.
    process = docker_util.run_in_docker(image, False, "/ip-control-loop")
    assert "KUBERNETES_SERVICE_HOST" in process.stderr

    # check script. It expects serviceaccount token to exist.
    process = docker_util.run_in_docker(image, False, "/install-cni.sh")
    "cat: /var/run/secrets/kubernetes.io/serviceaccount/token: No such file or directory" in process.stderr

    # whereabouts:0.5.4 also has a /ip-reconciler
    if version == "0.5.4":
        process = docker_util.run_in_docker(image, False, "/ip-reconciler")
        expected_message = "failed to instantiate the Kubernetes client"
        assert expected_message in process.stderr


def test_whereabouts_rock_0_6_3():
    _test_whereabouts_rock("ROCK_WHEREABOUTS_0_6_3", ROCK_EXPECTED_FILES)


def test_whereabouts_rock_0_6_1():
    _test_whereabouts_rock("ROCK_WHEREABOUTS_0_6_1", ROCK_EXPECTED_FILES)


def test_whereabouts_rock_0_5_4():
    _test_whereabouts_rock("ROCK_WHEREABOUTS_0_5_4", ROCK_EXPECTED_FILES + ["/ip-reconciler"])
