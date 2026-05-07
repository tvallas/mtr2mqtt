"""
Tests for container build hardening.
"""

from pathlib import Path


def test_final_image_upgrades_pip_before_installing_wheels():
    """
    The runtime image must not keep the vulnerable pip bundled with the base image.
    """
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    final_stage = dockerfile.split("FROM python:3.14-alpine", maxsplit=2)[-1]

    assert "python -m pip install --no-cache-dir --upgrade pip" in final_stage
    assert final_stage.index("--upgrade pip") < final_stage.index("/tmp/wheels/*.whl")
