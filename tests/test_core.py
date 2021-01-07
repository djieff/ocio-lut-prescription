"""core functions related tests
"""
from ocio_lut_prescription import core

OCIOBAKELUT_CMD = [
    "ociobakelut",
    "--iconfig",
    "/path/to/config.ocio",
    "--inputspace",
    "test_input_space",
    "--outputspace",
    "test_output_space",
    "--format",
    "cinespace",
    "/var/tmp/mylut.csp",
]

OCIO_REPORT = """--------- LUT prescription below -----------
OCIO: /path/to/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/mylut.csp

Executed command: ociobakelut --iconfig /path/to/config.ocio --inputspace test_input_space --outputspace test_output_space --format cinespace /var/tmp/mylut.csp
--------------------------------------------"""


def test_get_ociobakelut_cmd():
    """"""
    bake_cmd_data = {
        "ociobakelut_binary": "ociobakelut",
        "ocio_config": ["--iconfig", "/path/to/config.ocio"],
        "input_space": ["--inputspace", "test_input_space"],
        "lut_format": ["--format", "cinespace"],
        "lut_ext": "csp",
        "output_space": ["--outputspace", "test_output_space"],
        "lut_filename": "/var/tmp/mylut.csp",
    }
    cmd = core.get_ociobakelut_cmd(bake_cmd_data)
    assert cmd == OCIOBAKELUT_CMD


def test_ocio_report():
    """"""
    bake_cmd_data = {
        "ociobakelut_binary": "ociobakelut",
        "ocio_config": ["--iconfig", "/path/to/config.ocio"],
        "input_space": ["--inputspace", "test_input_space"],
        "lut_format": ["--format", "cinespace"],
        "lut_ext": "csp",
        "output_space": ["--outputspace", "test_output_space"],
        "lut_filename": "/var/tmp/mylut.csp",
    }

    report = core.ocio_report(bake_cmd_data, OCIOBAKELUT_CMD)
    assert report == OCIO_REPORT
