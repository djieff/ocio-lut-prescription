"""ocio python module of ocio_lut_prescription
"""
from typing import Any, Generator

import PyOpenColorIO as OCIO


def create_ocio_config_object(ocio_config_path: str) -> OCIO.Config:
    """create an ocio config object"""
    try:
        ocio_config_obj = OCIO.Config.CreateFromFile(ocio_config_path)
    except OCIO.Exception as err:
        raise err
    return ocio_config_obj


def get_colorspaces_names_list(
    ocio_config_obj: OCIO.Config,
) -> Generator[Any, Any, None]:
    """Retrieve the colorspace names from the OCIO configuration object"""
    return (colorspace_name for colorspace_name in ocio_config_obj.getColorSpaceNames())


def get_looks_names_list(ocio_config_obj: OCIO.Config) -> Generator[Any, Any, None]:
    """Retrieve the look names from the OCIO configuration object"""
    return (look_name for look_name in ocio_config_obj.getLookNames())


def get_displays_list(ocio_config_obj: OCIO.Config) -> Generator[Any, Any, None]:
    """Retrieve the display names from the OCIO configuration object"""
    return (display for display in ocio_config_obj.getDisplays())
