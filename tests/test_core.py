"""core functions related tests
"""
from dataclasses import replace
import pytest
from tests._constants import BAKE_TEMPLATES
from ocio_lut_prescription import core
from ocio_lut_prescription.core.ui import BakeCmdData


@pytest.mark.parametrize(
    "data, report",
    [
        (BAKE_TEMPLATES["default"]["data"], BAKE_TEMPLATES["default"]["report"]),
        (BAKE_TEMPLATES["icc"]["data"], BAKE_TEMPLATES["icc"]["report"]),
        (
            BAKE_TEMPLATES["override_lut_filename"]["data"],
            BAKE_TEMPLATES["override_lut_filename"]["report"],
        ),
        (
            BAKE_TEMPLATES["override_env"]["data"],
            BAKE_TEMPLATES["override_env"]["report"],
        ),
        (
            BAKE_TEMPLATES["use_cube_shaper_size"]["data"],
            BAKE_TEMPLATES["use_cube_shaper_size"]["report"],
        ),
        (
            BAKE_TEMPLATES["use_shaper_colorspace"]["data"],
            BAKE_TEMPLATES["use_shaper_colorspace"]["report"],
        ),
        (
            BAKE_TEMPLATES["use_looks"]["data"],
            BAKE_TEMPLATES["use_looks"]["report"],
        ),
    ],
)
def test_ocio_reports(data: tuple, report: str):
    """Test all the provided lut scenarios"""
    bake_cmd_data = BakeCmdData(*data)
    lut_name_param = {"lut_filename": core.get_lut_filename(bake_cmd_data)}
    bake_cmd_data = replace(bake_cmd_data, **lut_name_param)
    ociobakelut_cmd = core.get_ociobakelut_cmd(bake_cmd_data)
    report_result = core.ocio_report(bake_cmd_data, ociobakelut_cmd)
    assert report == report_result
