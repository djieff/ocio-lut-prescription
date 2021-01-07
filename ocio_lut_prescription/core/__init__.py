"""module containing core functions
"""
import os


def get_ociobakelut_cmd(bake_cmd_data: dict) -> list:
    """"""
    cmd = [bake_cmd_data["ociobakelut_binary"]]
    cmd.extend(bake_cmd_data["ocio_config"])
    cmd.extend(bake_cmd_data["input_space"])
    cmd.extend(bake_cmd_data.get("shaper_space", ""))
    cmd.extend(bake_cmd_data.get("output_space", bake_cmd_data.get("looks")))
    cmd.extend(bake_cmd_data["lut_format"])
    cmd.extend(bake_cmd_data.get("cube_size", ""))
    cmd.extend(bake_cmd_data.get("shaper_size", ""))

    if bake_cmd_data["lut_format"] == "icc":
        cmd.extend(bake_cmd_data.get("icc_white_point", ""))
        cmd.extend(bake_cmd_data.get("icc_displays", ""))
        cmd.extend(bake_cmd_data.get("icc_description", ""))
        cmd.extend(bake_cmd_data.get("icc_copyright", ""))

    cmd.append(bake_cmd_data["lut_filename"])

    return cmd


def ocio_report(bake_cmd_data: dict, ociobakelut_cmd: list) -> str:
    """"""
    return f"""--------- LUT prescription below -----------
OCIO: {bake_cmd_data['ocio_config'][1]}
SEQ: {os.environ.get('SEQ', 'N/A')}
SHOT: {os.environ.get('SHOT', 'N/A')}
Input ColorSpace: {bake_cmd_data['input_space'][1]}
Shaper ColorSpace: {bake_cmd_data.get('shaper_space', ['', 'N/A'])[1]}
Output ColorSpace: {bake_cmd_data.get('output_space', ['', 'N/A'])[1]}
Look: {bake_cmd_data.get('looks', ['', 'N/A'])[1]}

LUT Location: {bake_cmd_data['lut_filename']}

Executed command: {' '.join(ociobakelut_cmd)}
--------------------------------------------"""
