"""constants used for tests"""

BAKE_TEMPLATES = {
    "default": {
        "data": (
            "ociobakelut",
            "/path/to/test/config.ocio",
            "",
            "",
            "test_input_space",
            False,
            "test_shaper_space",
            True,
            "test_output_space",
            False,
            "",
            False,
            "33",
            False,
            "33",
            "cinespace",
            "csp",
            False,
            "",
            False,
            "",
            False,
            "",
            False,
            "",
            "/var/tmp",
            False,
            "",
            "",
        ),
        "report": """--------- LUT prescription below -----------
OCIO: /path/to/test/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/test_input_space_to_test_output_space.csp

Executed command: ociobakelut --iconfig /path/to/test/config.ocio --inputspace test_input_space --outputspace test_output_space --format cinespace /var/tmp/test_input_space_to_test_output_space.csp
--------------------------------------------""",
    },
    "icc": {
        "data": (
            "ociobakelut",
            "/path/to/test/config.ocio",
            "",
            "",
            "test_input_space",
            False,
            "test_shaper_space",
            True,
            "test_output_space",
            False,
            "",
            False,
            "33",
            False,
            "33",
            "icc",
            "icc",
            True,
            "6700",
            True,
            "test_icc_display",
            True,
            "test icc profile",
            True,
            "djieffx",
            "/var/tmp",
            False,
            "",
            "",
        ),
        "report": """--------- LUT prescription below -----------
OCIO: /path/to/test/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/test_input_space_to_test_output_space_D6700_displayICC-test_icc_display.icc

Executed command: ociobakelut --iconfig /path/to/test/config.ocio --inputspace test_input_space --outputspace test_output_space --format icc --whitepoint 6700 --displayicc test_icc_display --description test icc profile --copyright djieffx /var/tmp/test_input_space_to_test_output_space_D6700_displayICC-test_icc_display.icc
--------------------------------------------""",
    },
    "override_lut_filename": {
        "data": (
            "ociobakelut",
            "/path/to/test/config.ocio",
            "",
            "",
            "test_input_space",
            False,
            "test_shaper_space",
            True,
            "test_output_space",
            False,
            "",
            False,
            "33",
            False,
            "33",
            "cinespace",
            "csp",
            False,
            "6700",
            False,
            "test_icc_display",
            False,
            "test icc profile",
            False,
            "djieffx",
            "/var/tmp",
            True,
            "test_override",
            "",
        ),
        "report": """--------- LUT prescription below -----------
OCIO: /path/to/test/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/test_override.csp

Executed command: ociobakelut --iconfig /path/to/test/config.ocio --inputspace test_input_space --outputspace test_output_space --format cinespace /var/tmp/test_override.csp
--------------------------------------------""",
    },
    "override_env": {
        "data": (
            "ociobakelut",
            "/path/to/test/config.ocio",
            "seqA",
            "shotA",
            "test_input_space",
            False,
            "test_shaper_space",
            True,
            "test_output_space",
            False,
            "",
            False,
            "33",
            False,
            "33",
            "cinespace",
            "csp",
            False,
            "",
            False,
            "",
            False,
            "",
            False,
            "",
            "/var/tmp",
            False,
            "",
            "",
        ),
        "report": """--------- LUT prescription below -----------
OCIO: /path/to/test/config.ocio
SEQ: seqA
SHOT: shotA
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/seq-seqA_shot-shotA_test_input_space_to_test_output_space.csp

Executed command: ociobakelut --iconfig /path/to/test/config.ocio --inputspace test_input_space --outputspace test_output_space --format cinespace /var/tmp/seq-seqA_shot-shotA_test_input_space_to_test_output_space.csp
--------------------------------------------""",
    },
    "use_cube_shaper_size": {
        "data": (
            "ociobakelut",
            "/path/to/test/config.ocio",
            "",
            "",
            "test_input_space",
            False,
            "test_shaper_space",
            True,
            "test_output_space",
            False,
            "",
            True,
            "33",
            True,
            "44",
            "cinespace",
            "csp",
            False,
            "",
            False,
            "",
            False,
            "",
            False,
            "",
            "/var/tmp",
            False,
            "",
            "",
        ),
        "report": """--------- LUT prescription below -----------
OCIO: /path/to/test/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/test_input_space_to_test_output_space_c33_s44.csp

Executed command: ociobakelut --iconfig /path/to/test/config.ocio --inputspace test_input_space --outputspace test_output_space --format cinespace --cubesize 33 --shapersize 44 /var/tmp/test_input_space_to_test_output_space_c33_s44.csp
--------------------------------------------""",
    },
    "use_shaper_colorspace": {
        "data": (
            "ociobakelut",
            "/path/to/test/config.ocio",
            "",
            "",
            "test_input_space",
            True,
            "test_shaper_space",
            True,
            "test_output_space",
            False,
            "",
            False,
            "33",
            False,
            "33",
            "cinespace",
            "csp",
            False,
            "",
            False,
            "",
            False,
            "",
            False,
            "",
            "/var/tmp",
            False,
            "",
            "",
        ),
        "report": """--------- LUT prescription below -----------
OCIO: /path/to/test/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: test_shaper_space
Output ColorSpace: test_output_space
Look: N/A

LUT Location: /var/tmp/test_input_space_shaper-test_shaper_space_to_test_output_space.csp

Executed command: ociobakelut --iconfig /path/to/test/config.ocio --inputspace test_input_space --shaperspace test_shaper_space --outputspace test_output_space --format cinespace /var/tmp/test_input_space_shaper-test_shaper_space_to_test_output_space.csp
--------------------------------------------""",
    },
    "use_looks": {
        "data": (
            "ociobakelut",
            "/path/to/test/config.ocio",
            "",
            "",
            "test_input_space",
            False,
            "test_shaper_space",
            False,
            "test_output_space",
            True,
            "test_look",
            False,
            "33",
            False,
            "33",
            "cinespace",
            "csp",
            False,
            "",
            False,
            "",
            False,
            "",
            False,
            "",
            "/var/tmp",
            False,
            "",
            "",
        ),
        "report": """--------- LUT prescription below -----------
OCIO: /path/to/test/config.ocio
SEQ: N/A
SHOT: N/A
Input ColorSpace: test_input_space
Shaper ColorSpace: N/A
Output ColorSpace: N/A
Look: test_look

LUT Location: /var/tmp/test_input_space_to_test_look.csp

Executed command: ociobakelut --iconfig /path/to/test/config.ocio --inputspace test_input_space --looks test_look --format cinespace /var/tmp/test_input_space_to_test_look.csp
--------------------------------------------""",
    },
}
