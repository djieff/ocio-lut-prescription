"""constants used for tests"""

LUT_SCENARIOS = {
    "default": {
        "bake_cmd_data": {
            "ociobakelut_bin": "ociobakelut",
            "ocio_config": "/path/to/test/config.ocio",
            "env_seq": "",
            "env_shot": "",
            "input_space": "test_input_space",
            "use_shaper_space": False,
            "shaper_space": "test_shaper_space",
            "use_output_space": True,
            "output_space": "test_output_space",
            "use_looks": False,
            "looks": "",
            "use_cube_size": False,
            "cube_size": "33",
            "use_shaper_size": False,
            "shaper_size": "33",
            "lut_format": "cinespace",
            "lut_ext": "csp",
            "use_icc_white_point": False,
            "icc_white_point": "",
            "use_icc_displays": False,
            "icc_displays": "",
            "use_icc_description": False,
            "icc_description": "",
            "use_icc_copyright": False,
            "icc_copyright": "",
            "output_dir": "/var/tmp",
            "use_override_lut_filename": False,
            "override_lut_filename": "",
        },
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
        "bake_cmd_data": {
            "ociobakelut_bin": "ociobakelut",
            "ocio_config": "/path/to/test/config.ocio",
            "env_seq": "",
            "env_shot": "",
            "input_space": "test_input_space",
            "use_shaper_space": False,
            "shaper_space": "test_shaper_space",
            "use_output_space": True,
            "output_space": "test_output_space",
            "use_looks": False,
            "looks": "",
            "use_cube_size": False,
            "cube_size": "33",
            "use_shaper_size": False,
            "shaper_size": "33",
            "lut_format": "icc",
            "lut_ext": "icc",
            "use_icc_white_point": True,
            "icc_white_point": "6700",
            "use_icc_displays": True,
            "icc_displays": "test_icc_display",
            "use_icc_description": True,
            "icc_description": "test icc profile",
            "use_icc_copyright": True,
            "icc_copyright": "djieffx",
            "output_dir": "/var/tmp",
            "use_override_lut_filename": False,
            "override_lut_filename": "",
        },
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
        "bake_cmd_data": {
            "ociobakelut_bin": "ociobakelut",
            "ocio_config": "/path/to/test/config.ocio",
            "env_seq": "",
            "env_shot": "",
            "input_space": "test_input_space",
            "use_shaper_space": False,
            "shaper_space": "test_shaper_space",
            "use_output_space": True,
            "output_space": "test_output_space",
            "use_looks": False,
            "looks": "",
            "use_cube_size": False,
            "cube_size": "33",
            "use_shaper_size": False,
            "shaper_size": "33",
            "lut_format": "cinespace",
            "lut_ext": "csp",
            "use_icc_white_point": False,
            "icc_white_point": "6700",
            "use_icc_displays": False,
            "icc_displays": "test_icc_display",
            "use_icc_description": False,
            "icc_description": "test icc profile",
            "use_icc_copyright": False,
            "icc_copyright": "djieffx",
            "output_dir": "/var/tmp",
            "use_override_lut_filename": True,
            "override_lut_filename": "test_override",
        },
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
        "bake_cmd_data": {
            "ociobakelut_bin": "ociobakelut",
            "ocio_config": "/path/to/test/config.ocio",
            "env_seq": "seqA",
            "env_shot": "shotA",
            "input_space": "test_input_space",
            "use_shaper_space": False,
            "shaper_space": "test_shaper_space",
            "use_output_space": True,
            "output_space": "test_output_space",
            "use_looks": False,
            "looks": "",
            "use_cube_size": False,
            "cube_size": "33",
            "use_shaper_size": False,
            "shaper_size": "33",
            "lut_format": "cinespace",
            "lut_ext": "csp",
            "use_icc_white_point": False,
            "icc_white_point": "",
            "use_icc_displays": False,
            "icc_displays": "",
            "use_icc_description": False,
            "icc_description": "",
            "use_icc_copyright": False,
            "icc_copyright": "",
            "output_dir": "/var/tmp",
            "use_override_lut_filename": False,
            "override_lut_filename": "",
        },
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
        "bake_cmd_data": {
            "ociobakelut_bin": "ociobakelut",
            "ocio_config": "/path/to/test/config.ocio",
            "env_seq": "",
            "env_shot": "",
            "input_space": "test_input_space",
            "use_shaper_space": False,
            "shaper_space": "test_shaper_space",
            "use_output_space": True,
            "output_space": "test_output_space",
            "use_looks": False,
            "looks": "",
            "use_cube_size": True,
            "cube_size": "33",
            "use_shaper_size": True,
            "shaper_size": "44",
            "lut_format": "cinespace",
            "lut_ext": "csp",
            "use_icc_white_point": False,
            "icc_white_point": "",
            "use_icc_displays": False,
            "icc_displays": "",
            "use_icc_description": False,
            "icc_description": "",
            "use_icc_copyright": False,
            "icc_copyright": "",
            "output_dir": "/var/tmp",
            "use_override_lut_filename": False,
            "override_lut_filename": "",
        },
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
        "bake_cmd_data": {
            "ociobakelut_bin": "ociobakelut",
            "ocio_config": "/path/to/test/config.ocio",
            "env_seq": "",
            "env_shot": "",
            "input_space": "test_input_space",
            "use_shaper_space": True,
            "shaper_space": "test_shaper_space",
            "use_output_space": True,
            "output_space": "test_output_space",
            "use_looks": False,
            "looks": "",
            "use_cube_size": False,
            "cube_size": "33",
            "use_shaper_size": False,
            "shaper_size": "33",
            "lut_format": "cinespace",
            "lut_ext": "csp",
            "use_icc_white_point": False,
            "icc_white_point": "",
            "use_icc_displays": False,
            "icc_displays": "",
            "use_icc_description": False,
            "icc_description": "",
            "use_icc_copyright": False,
            "icc_copyright": "",
            "output_dir": "/var/tmp",
            "use_override_lut_filename": False,
            "override_lut_filename": "",
        },
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
        "bake_cmd_data": {
            "ociobakelut_bin": "ociobakelut",
            "ocio_config": "/path/to/test/config.ocio",
            "env_seq": "",
            "env_shot": "",
            "input_space": "test_input_space",
            "use_shaper_space": False,
            "shaper_space": "test_shaper_space",
            "use_output_space": False,
            "output_space": "test_output_space",
            "use_looks": True,
            "looks": "test_look",
            "use_cube_size": False,
            "cube_size": "33",
            "use_shaper_size": False,
            "shaper_size": "33",
            "lut_format": "cinespace",
            "lut_ext": "csp",
            "use_icc_white_point": False,
            "icc_white_point": "",
            "use_icc_displays": False,
            "icc_displays": "",
            "use_icc_description": False,
            "icc_description": "",
            "use_icc_copyright": False,
            "icc_copyright": "",
            "output_dir": "/var/tmp",
            "use_override_lut_filename": False,
            "override_lut_filename": "",
        },
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
