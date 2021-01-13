"""core functions related tests
"""
import pytest
from tests._constants import LUT_SCENARIOS
from ocio_lut_prescription import core


@pytest.mark.parametrize(
    "bake_cmd_data, report",
    [
        (LUT_SCENARIOS["default"]["bake_cmd_data"], LUT_SCENARIOS["default"]["report"]),
        (LUT_SCENARIOS["icc"]["bake_cmd_data"], LUT_SCENARIOS["icc"]["report"]),
        (
            LUT_SCENARIOS["override_lut_filename"]["bake_cmd_data"],
            LUT_SCENARIOS["override_lut_filename"]["report"],
        ),
        (
            LUT_SCENARIOS["override_env"]["bake_cmd_data"],
            LUT_SCENARIOS["override_env"]["report"],
        ),
        (
            LUT_SCENARIOS["use_cube_shaper_size"]["bake_cmd_data"],
            LUT_SCENARIOS["use_cube_shaper_size"]["report"],
        ),
        (
            LUT_SCENARIOS["use_shaper_colorspace"]["bake_cmd_data"],
            LUT_SCENARIOS["use_shaper_colorspace"]["report"],
        ),
        (
            LUT_SCENARIOS["use_looks"]["bake_cmd_data"],
            LUT_SCENARIOS["use_looks"]["report"],
        ),
    ],
)
def test_ocio_reports(bake_cmd_data: dict, report: str):
    """Test all the provided lut scenarios"""
    bake_cmd_data["lut_filename"] = core.get_lut_filename(bake_cmd_data)
    ociobakelut_cmd = core.get_ociobakelut_cmd(bake_cmd_data)
    report_result = core.ocio_report(bake_cmd_data, ociobakelut_cmd)
    assert report == report_result
