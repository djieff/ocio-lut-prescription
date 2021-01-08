"""core functions related tests
"""
import pytest
from ocio_lut_prescription import core

LUT_SCENARIOS = {
    "default": {
        "bake_cmd_data": {
            "ociobakelut_binary": "ociobakelut",
            "ocio_config": ["--iconfig", "/path/to/config.ocio"],
            "input_space": ["--inputspace", "test_input_space"],
            "lut_format": ["--format", "cinespace"],
            "lut_ext": "csp",
            "output_space": ["--outputspace", "test_output_space"],
            "lut_filename": "/var/tmp/mylut.csp",
        },
        "report": """--------- LUT prescription below -----------
OCIO: /path/to/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/mylut.csp

Executed command: ociobakelut --iconfig /path/to/config.ocio --inputspace test_input_space --outputspace test_output_space --format cinespace /var/tmp/mylut.csp
--------------------------------------------""",
    },
    "icc": {
        "bake_cmd_data": {
            "ociobakelut_binary": "ociobakelut",
            "ocio_config": ["--iconfig", "/path/to/config.ocio"],
            "input_space": ["--inputspace", "test_input_space"],
            "lut_format": ["--format", "icc"],
            "lut_ext": "icc",
            "output_space": ["--outputspace", "test_output_space"],
            "lut_filename": "/var/tmp/mylut.icc",
            "icc_white_point": ["--whitepoint", "7000"],
            "icc_displays": ["--displayicc", "test_display"],
            "icc_copyright": ["--copyright", "test_copyright_info"],
            "icc_description": ["--description", "test_description_info"],
        },
        "report": """--------- LUT prescription below -----------
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
    },
}


@pytest.mark.parametrize(
    "bake_cmd_data, report", [
        (
                LUT_SCENARIOS["default"]["bake_cmd_data"],
                LUT_SCENARIOS["default"]["report"]
        ),
        (
                LUT_SCENARIOS["icc"]["bake_cmd_data"],
                LUT_SCENARIOS["icc"]["report"]
        )
    ]
)
def test_ocio_reports(bake_cmd_data, report):
    """Test all the provided lut scenarios"""
    ociobakelut_cmd = core.get_ociobakelut_cmd(bake_cmd_data)
    report_result = core.ocio_report(bake_cmd_data, ociobakelut_cmd)
    assert report == report_result
