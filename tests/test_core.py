# pylint: disable=redefined-outer-name
"""core functions related tests
"""
import pytest
from ocio_lut_prescription import core


@pytest.fixture
def default_bake_cmd_data():
    """"""
    return {
        "ociobakelut_binary": "ociobakelut",
        "ocio_config": ["--iconfig", "/path/to/config.ocio"],
        "input_space": ["--inputspace", "test_input_space"],
        "lut_format": ["--format", "cinespace"],
        "lut_ext": "csp",
        "output_space": ["--outputspace", "test_output_space"],
        "lut_filename": "/var/tmp/mylut.csp",
    }


@pytest.fixture
def default_report():
    """"""
    return """--------- LUT prescription below -----------
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


@pytest.fixture
def icc_bake_cmd_data(default_bake_cmd_data):
    """"""
    icc_bake_cmd_data = default_bake_cmd_data
    icc_bake_cmd_data["lut_format"] = ["--format", "icc"]
    icc_bake_cmd_data["lut_ext"] = "icc"
    icc_bake_cmd_data["lut_filename"] = "/var/tmp/mylut.icc"
    icc_bake_cmd_data["icc_white_point"] = ["--whitepoint", "7000"]
    icc_bake_cmd_data["icc_displays"] = ["--displayicc", "test_display"]
    icc_bake_cmd_data["icc_copyright"] = ["--copyright", "test_copyright_info"]
    icc_bake_cmd_data["icc_description"] = ["--description", "test_description_info"]

    return icc_bake_cmd_data


@pytest.fixture
def icc_report():
    """"""
    return """--------- LUT prescription below -----------
OCIO: /path/to/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/mylut.icc

Executed command: ociobakelut --iconfig /path/to/config.ocio --inputspace test_input_space --outputspace test_output_space --format icc --whitepoint 7000 --displayicc test_display --description test_description_info --copyright test_copyright_info /var/tmp/mylut.icc
--------------------------------------------"""


@pytest.mark.parametrize(
    "base_bake_cmd_data, base_report",
    [("default_bake_cmd_data", "default_report"), ("icc_bake_cmd_data", "icc_report")],
)
def test_ocio_reports(base_bake_cmd_data, base_report, request):
    """"""
    bake_cmd_data = request.getfixturevalue(base_bake_cmd_data)
    expected_report = request.getfixturevalue(base_report)

    ociobakelut_cmd = core.get_ociobakelut_cmd(bake_cmd_data)
    report = core.ocio_report(bake_cmd_data, ociobakelut_cmd)
    assert report == expected_report
