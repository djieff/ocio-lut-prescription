"""module containing core functions
"""
import os


def get_lut_filename(bake_cmd_data: dict) -> str:

    output_dir = bake_cmd_data["output_dir"]

    lut_radical = (
        bake_cmd_data["override_lut_filename"]
        if bake_cmd_data["use_override_lut_filename"]
        else get_lut_radical(bake_cmd_data)
    )

    return os.path.join(output_dir, ".".join([lut_radical, bake_cmd_data["lut_ext"]]))


def get_lut_radical(bake_cmd_data: dict) -> str:
    return "".join(
        [
            get_colorspace_input_prefix(bake_cmd_data),
            "_to_",
            get_lut_color_output_suffix(bake_cmd_data),
        ]
    )


def get_colorspace_input_prefix(bake_cmd_data: dict) -> str:
    env_prefix = "".join(
        [
            f"seq-{bake_cmd_data['env_seq']}_" if bake_cmd_data["env_seq"] else "",
            f"shot-{bake_cmd_data['env_shot']}_" if bake_cmd_data["env_shot"] else "",
        ]
    )

    input_prefix = bake_cmd_data["input_space"].replace(" ", "_")

    shaper_prefix = (
        f"_shaper-{bake_cmd_data['shaper_space'].replace(' ', '_')}"
        if bake_cmd_data["use_shaper_space"]
        else ""
    )

    return "".join([env_prefix, input_prefix, shaper_prefix])


def get_lut_color_output_suffix(bake_cmd_data: dict) -> str:
    output_suffix = (
        f"{bake_cmd_data['output_space'].replace(' ', '_')}_"
        if bake_cmd_data["use_output_space"]
        else f"{bake_cmd_data['looks']}_"
    )
    cube_size_suffix = (
        f"c{bake_cmd_data['cube_size']}_" if bake_cmd_data["use_cube_size"] else ""
    )
    shaper_size_suffix = (
        f"s{bake_cmd_data['shaper_size']}_" if bake_cmd_data["use_shaper_size"] else ""
    )
    icc_only_suffix = "".join(
        [
            f"D{bake_cmd_data['icc_white_point']}_"
            if bake_cmd_data["icc_white_point"] and bake_cmd_data["use_icc_white_point"]
            else "",
            f"displayICC-{bake_cmd_data['icc_displays'].replace(' ', '_')}_"
            if bake_cmd_data["icc_displays"] and bake_cmd_data["use_icc_displays"]
            else "",
        ]
        if bake_cmd_data["lut_ext"] == "icc"
        else ""
    )

    return "".join(
        [
            output_suffix,
            cube_size_suffix,
            shaper_size_suffix,
            icc_only_suffix,
        ]
    ).rstrip("_")


def get_ociobakelut_cmd(bake_cmd_data: dict) -> list:
    cmd = [bake_cmd_data["ociobakelut_bin"]]
    cmd.extend(["--iconfig", bake_cmd_data["ocio_config"]])
    cmd.extend(["--inputspace", bake_cmd_data["input_space"]])

    if bake_cmd_data["use_shaper_space"] and bake_cmd_data["shaper_space"]:
        cmd.extend(["--shaperspace", bake_cmd_data["shaper_space"]])
    if bake_cmd_data["use_output_space"] and bake_cmd_data["output_space"]:
        cmd.extend(["--outputspace", bake_cmd_data["output_space"]])
    if bake_cmd_data["use_looks"] and bake_cmd_data["looks"]:
        cmd.extend(["--looks", bake_cmd_data["looks"]])

    cmd.extend(["--format", bake_cmd_data["lut_format"]])

    if bake_cmd_data["use_cube_size"] and bake_cmd_data["cube_size"]:
        cmd.extend(["--cubesize", bake_cmd_data["cube_size"]])

    if bake_cmd_data["use_shaper_size"] and bake_cmd_data["shaper_size"]:
        cmd.extend(["--shapersize", bake_cmd_data["shaper_size"]])

    if bake_cmd_data["lut_ext"] == "icc":
        if bake_cmd_data["use_icc_white_point"] and bake_cmd_data["icc_white_point"]:
            cmd.extend(["--whitepoint", bake_cmd_data["icc_white_point"]])
        if bake_cmd_data["use_icc_displays"] and bake_cmd_data["icc_displays"]:
            cmd.extend(["--displayicc", bake_cmd_data["icc_displays"]])
        if bake_cmd_data["use_icc_description"] and bake_cmd_data["icc_description"]:
            cmd.extend(["--description", bake_cmd_data["icc_description"]])
        if bake_cmd_data["use_icc_copyright"] and bake_cmd_data["icc_copyright"]:
            cmd.extend(["--copyright", bake_cmd_data["icc_copyright"]])

    cmd.extend([bake_cmd_data["lut_filename"]])

    return cmd


def ocio_report(bake_cmd_data: dict, ociobakelut_cmd: list) -> str:
    return f"""--------- LUT prescription below -----------
OCIO: {bake_cmd_data['ocio_config']}
SEQ: {bake_cmd_data['env_seq'] if bake_cmd_data['env_seq'] else 'N/A'}
SHOT: {bake_cmd_data['env_shot'] if bake_cmd_data['env_shot'] else 'N/A'}
Input ColorSpace: {bake_cmd_data['input_space']}
Shaper ColorSpace: {bake_cmd_data['shaper_space'] if bake_cmd_data['use_shaper_space'] else 'N/A'}
Output ColorSpace: {bake_cmd_data['output_space'] if bake_cmd_data['use_output_space'] else 'N/A'}
Look: {bake_cmd_data['looks'] if bake_cmd_data['use_looks'] else 'N/A'}

LUT Location: {bake_cmd_data['lut_filename']}

Executed command: {' '.join(ociobakelut_cmd)}
--------------------------------------------"""
