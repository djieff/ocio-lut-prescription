# pylint: disable=expression-not-assigned, too-many-arguments, too-many-locals, no-name-in-module
"""ui related submodule of the core module"""
import os
import re
from typing import Any, Generator

from PySide2.QtCore import Qt, QSettings
from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication, QFileDialog, QMainWindow

from ocio_lut_prescription.core import ocio

LUT_INFO_REGEX = re.compile(r"^(?P<lut_format>\w+) \(.(?P<lut_ext>\w{3})\)$")
SIZES_LIST = [str(x) for x in range(1, 67)]


def load_ocio_config(main_window: QMainWindow, settings: QSettings):
    """"""
    ocio_config_path = main_window.ocioCfgLineEdit.text()

    if ocio_config_path:
        ocio_config_obj = ocio.create_ocio_config_object(ocio_config_path)

        input_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        shaper_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        output_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        looks_generator = ocio.get_looks_names_list(ocio_config_obj)
        displays_generator = ocio.get_displays_list(ocio_config_obj)

        if ocio_config_obj:
            initialize_ui_with_config_data(
                main_window,
                input_colorspaces_generator,
                shaper_colorspaces_generator,
                output_colorspaces_generator,
                looks_generator,
                displays_generator,
            )
            save_settings(settings, main_window)


def settings_clear(app: QApplication, settings: QSettings, main_window: QMainWindow):
    """"""
    set_system_style(app, settings)
    initialize_ui_default(main_window)
    settings.clear()


def save_style_settings(settings: QSettings, style=None):
    """"""
    settings.setValue("misc/style", style)
    settings.sync()


def save_settings(settings: QSettings, main_window: QMainWindow):
    """"""
    settings.setValue("ocio/config_path", main_window.ocioCfgLineEdit.text())
    settings.setValue(
        "colorspaces/input", main_window.inputColorSpacesComboBox.currentText()
    )
    settings.setValue(
        "colorspaces/shaper", main_window.shaperColorSpacesComboBox.currentText()
    )
    settings.setValue(
        "colorspaces/output", main_window.outputColorSpacesComboBox.currentText()
    )
    settings.setValue("colorspaces/looks", main_window.looksComboBox.currentText())
    settings.setValue("output/directory", main_window.outputDirLineEdit.text())
    settings.setValue("baking/lut_format", main_window.lutFormatComboBox.currentText())
    settings.setValue("baking/cube_size", main_window.cubeSizeComboBox.currentText())
    settings.setValue(
        "baking/shaper_size", main_window.shaperSizeComboBox.currentText()
    )
    settings.setValue("icc/white_point", main_window.iccWhitePointLineEdit.text())
    settings.setValue("icc/displays", main_window.iccDisplaysComboBox.currentText())
    settings.setValue("icc/description", main_window.iccDescriptionLineEdit.text())
    settings.setValue("icc/copyright", main_window.iccCopyrightLineEdit.text())
    settings.sync()


def load_settings(app: QApplication, settings: QSettings, main_window: QMainWindow):
    """"""
    combo_box_settings = {
        main_window.inputColorSpacesComboBox: "colorspaces/input",
        main_window.shaperColorSpacesComboBox: "colorspaces/shaper",
        main_window.outputColorSpacesComboBox: "colorspaces/output",
        main_window.looksComboBox: "colorspaces/looks",
        main_window.lutFormatComboBox: "baking/lut_format",
        main_window.cubeSizeComboBox: "baking/cube_size",
        main_window.shaperSizeComboBox: "baking/shaper_size",
        main_window.iccDisplaysComboBox: "icc/displays",
    }
    line_edit_settings = {
        main_window.iccWhitePointLineEdit: "icc/white_point",
        main_window.iccDescriptionLineEdit: "icc/description",
        main_window.iccCopyrightLineEdit: "icc/copyright",
        main_window.outputDirLineEdit: "output/directory",
    }

    if settings.value("misc/style") == "dark":
        set_dark_style(app, settings)

    ocio_config_path = settings.value("ocio/config_path")
    if not ocio_config_path:
        initialize_ui_default(main_window)
    else:
        initialize_ui(
            main_window,
            settings,
            combo_box_settings,
            line_edit_settings,
            ocio_config_path,
        )


def initialize_ui(
    main_window: QMainWindow,
    settings: QSettings,
    combo_box_settings: dict,
    line_edit_settings: dict,
    ocio_config_path: str,
):
    """"""
    main_window.ocioCfgLineEdit.setText(ocio_config_path)
    ocio_config_obj = ocio.create_ocio_config_object(ocio_config_path)
    if ocio_config_obj:
        input_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        shaper_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        output_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        looks_generator = ocio.get_looks_names_list(ocio_config_obj)
        displays_generator = ocio.get_displays_list(ocio_config_obj)

        initialize_ui_with_config_data(
            main_window,
            input_colorspaces_generator,
            shaper_colorspaces_generator,
            output_colorspaces_generator,
            looks_generator,
            displays_generator,
        )

        main_window.cubeSizeComboBox.addItems(SIZES_LIST)
        main_window.cubeSizeComboBox.setDisabled(True)
        main_window.shaperSizeComboBox.addItems(SIZES_LIST)
        main_window.shaperSizeComboBox.setDisabled(True)

        for widget, combobox_setting in combo_box_settings.items():
            index = widget.findText(
                settings.value(combobox_setting), Qt.MatchFixedString
            )
            if index >= 0:
                widget.setCurrentIndex(index)

        for widget, lineedit_setting in line_edit_settings.items():
            widget.setText(settings.value(lineedit_setting))

        check_for_icc(main_window, main_window.lutFormatComboBox.currentText())
        check_to_enable_baking(main_window)


def check_for_icc(main_window: QMainWindow, lut_format_combobox_text: str):
    """Enable ICC Options is icc format is selected"""
    if "icc" in lut_format_combobox_text:
        main_window.iccWhitePointCheckBox.setEnabled(True)
        main_window.iccDisplaysCheckBox.setEnabled(True)
        main_window.iccDescriptionCheckBox.setEnabled(True)
        main_window.iccCopyrightCheckBox.setEnabled(True)

        if main_window.iccWhitePointCheckBox.isChecked():
            main_window.iccWhitePointLineEdit.setEnabled(True)

        if main_window.iccDisplaysCheckBox.isChecked():
            main_window.iccDisplaysComboBox.setEnabled(True)

        if main_window.iccDescriptionCheckBox.isChecked():
            main_window.iccDescriptionLineEdit.setEnabled(True)

        if main_window.iccCopyrightCheckBox.isChecked():
            main_window.iccCopyrightLineEdit.setEnabled(True)

    else:
        main_window.iccWhitePointCheckBox.setDisabled(True)
        main_window.iccDisplaysCheckBox.setDisabled(True)
        main_window.iccDescriptionCheckBox.setDisabled(True)
        main_window.iccCopyrightCheckBox.setDisabled(True)

        main_window.iccWhitePointLineEdit.setDisabled(True)
        main_window.iccDisplaysComboBox.setDisabled(True)
        main_window.iccDescriptionLineEdit.setDisabled(True)
        main_window.iccCopyrightLineEdit.setDisabled(True)


def set_dark_style(app: QApplication, settings: QSettings):
    """"""
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    save_style_settings(settings, style="dark")


def set_system_style(app: QApplication, settings: QSettings):
    """"""
    palette = QPalette()
    app.setPalette(palette)
    save_style_settings(settings, style="system")


def browse_for_ocio_config(main_window: QMainWindow, settings: QSettings):
    """"""
    ocio_config = QFileDialog.getOpenFileName(
        caption="Select OCIO Configuration", filter="*.ocio"
    )[0]
    main_window.ocioCfgLineEdit.setText(ocio_config)
    save_settings(settings, main_window)


def browse_for_lut_output_dir(main_window: QMainWindow, settings: QSettings):
    """"""
    output_dir = QFileDialog.getExistingDirectory()
    main_window.outputDirLineEdit.setText(output_dir)
    check_to_enable_baking(main_window)
    save_settings(settings, main_window)


def check_to_enable_baking(main_window: QMainWindow):
    """"""
    radio_check = any(
        [
            bool(main_window.outputColorSpacesRadioButton.isChecked()),
            bool(main_window.looksRadioButton.isChecked()),
        ]
    )
    output_check = bool(main_window.outputDirLineEdit.text())

    main_window.processBakeLutPushButton.setEnabled(True) if all(
        [radio_check, output_check]
    ) else main_window.processBakeLutPushButton.setDisabled(True)


def initialize_ui_default(main_window: QMainWindow):
    """"""
    main_window.cubeSizeComboBox.clear()
    main_window.shaperSizeComboBox.clear()
    main_window.cubeSizeComboBox.addItems(SIZES_LIST)
    main_window.shaperSizeComboBox.addItems(SIZES_LIST)

    main_window.cubeSizeComboBox.setCurrentIndex(32)
    main_window.shaperSizeComboBox.setCurrentIndex(32)
    main_window.lutFormatComboBox.setCurrentIndex(0)

    main_window.inputColorSpacesComboBox.clear()
    main_window.shaperColorSpacesComboBox.clear()
    main_window.outputColorSpacesComboBox.clear()
    main_window.looksComboBox.clear()
    main_window.iccDisplaysComboBox.clear()
    main_window.ocioCfgLineEdit.clear()
    main_window.resultLineEdit.clear()
    main_window.resultLogTextEdit.clear()
    main_window.overrideLutNameLineEdit.clear()
    main_window.iccWhitePointLineEdit.clear()
    main_window.iccDescriptionLineEdit.clear()
    main_window.iccCopyrightLineEdit.clear()
    main_window.outputDirLineEdit.clear()

    main_window.processBakeLutPushButton.setDisabled(True)
    main_window.overrideLutNameCheckBox.setChecked(False)
    main_window.cubeSizeCheckBox.setChecked(False)
    main_window.shaperSizeCheckBox.setChecked(False)
    main_window.iccWhitePointCheckBox.setChecked(False)
    main_window.iccDisplaysCheckBox.setChecked(False)
    main_window.iccDescriptionCheckBox.setChecked(False)
    main_window.iccCopyrightCheckBox.setChecked(False)


def initialize_ui_with_config_data(
    main_window: QMainWindow,
    input_colorspaces_generator: Generator[Any, Any, None],
    shaper_colorspaces_generator: Generator[Any, Any, None],
    output_colorspaces_generator: Generator[Any, Any, None],
    looks_generator: Generator[Any, Any, None],
    displays_generator: Generator[Any, Any, None],
):
    """"""
    main_window.shaperColorSpacesCheckBox.setEnabled(True)
    main_window.outputColorSpacesRadioButton.setEnabled(True)
    main_window.looksRadioButton.setEnabled(True)

    main_window.inputColorSpacesComboBox.addItems(input_colorspaces_generator)
    main_window.shaperColorSpacesComboBox.addItems(shaper_colorspaces_generator)
    main_window.outputColorSpacesComboBox.addItems(output_colorspaces_generator)
    main_window.looksComboBox.addItems(looks_generator)
    main_window.iccDisplaysComboBox.addItems(displays_generator)

    main_window.cubeSizeComboBox.setCurrentIndex(32)
    main_window.shaperSizeComboBox.setCurrentIndex(32)

    main_window.inputColorSpacesComboBox.setEnabled(True)
    main_window.outputColorSpacesRadioButton.setChecked(True)

    check_to_enable_baking(main_window)


def generate_lut_filename(main_window: QMainWindow) -> str:
    """"""
    lut_info_match = re.match(
        LUT_INFO_REGEX, main_window.lutFormatComboBox.currentText()
    )
    lut_ext = lut_info_match.group("lut_ext")
    output_dir = main_window.outputDirLineEdit.text()

    lut_radical = (
        main_window.overrideLutNameLineEdit.text()
        if main_window.overrideLutNameCheckBox.isChecked()
        and main_window.overrideLutNameLineEdit.text()
        else build_lut_radical(main_window)
    )

    lut_filename = os.path.join(output_dir, ".".join([lut_radical, lut_ext]))

    return lut_filename


def build_lut_radical(main_window: QMainWindow) -> str:
    """"""
    return "_to_".join(
        [
            get_colorspace_input_prefix(main_window),
            get_lut_color_output_suffix(main_window),
        ]
    )


def get_colorspace_input_prefix(main_window: QMainWindow) -> str:
    """"""
    env_prefix = "".join(
        [
            f"seq-{main_window.ocioSeqLineEdit.text()}_"
            if main_window.ocioSeqLineEdit.text()
            else "",
            f"shot-{main_window.ocioShotLineEdit.text()}_"
            if main_window.ocioShotLineEdit.text()
            else "",
        ]
    )

    input_prefix = main_window.inputColorSpacesComboBox.currentText().replace(" ", "_")

    shaper_prefix = (
        f"_shaper-{main_window.shaperColorSpacesComboBox.currentText().replace(' ', '_')}"
        if main_window.shaperColorSpacesCheckBox.isChecked()
        else ""
    )

    return "".join([env_prefix, input_prefix, shaper_prefix])


def get_lut_color_output_suffix(main_window: QMainWindow) -> str:
    """"""
    output_suffix = (
        main_window.outputColorSpacesComboBox.currentText().replace(" ", "_") + "_"
        if main_window.outputColorSpacesComboBox.currentText()
        else main_window.looksComboBox.currentText().replace(" ", "_")
    )

    cube_size_suffix = (
        f"c{main_window.cubeSizeComboBox.currentText()}_"
        if main_window.cubeSizeCheckBox.checkState()
        else ""
    )

    shaper_size_suffix = (
        f"s{main_window.shaperSizeComboBox.currentText()}_"
        if main_window.shaperSizeCheckBox.checkState()
        else ""
    )

    icc_only_suffix = ""
    if main_window.lutFormatComboBox.currentText() == "icc (.icc)":
        icc_only_suffix = "".join(
            [
                f"D{main_window.iccWhitePointLineEdit.text()}_"
                if main_window.iccWhitePointCheckBox.isChecked()
                else "",
                f"displayICC-{main_window.iccDisplaysComboBox.currentText().replace(' ', '_')}_"
                if main_window.iccDisplaysCheckBox.isChecked()
                else "",
            ]
        )

    return "".join(
        [
            output_suffix,
            cube_size_suffix,
            shaper_size_suffix,
            icc_only_suffix,
        ]
    ).rstrip("_")


def get_bake_cmd_data(main_window: QMainWindow) -> dict:
    """"""
    ocio_config = main_window.ocioCfgLineEdit.text()
    input_space = main_window.inputColorSpacesComboBox.currentText()
    shaper_space = main_window.shaperColorSpacesComboBox.currentText()
    output_space = main_window.outputColorSpacesComboBox.currentText()
    looks = main_window.looksComboBox.currentText()
    cube_size = main_window.cubeSizeComboBox.currentText()
    shaper_size = main_window.shaperSizeComboBox.currentText()
    icc_white_point = main_window.iccWhitePointLineEdit.text()
    icc_displays = main_window.iccDisplaysComboBox.currentText()
    icc_description = main_window.iccDescriptionLineEdit.text()
    icc_copyright = main_window.iccCopyrightLineEdit.text()

    lut_info_match = re.match(
        LUT_INFO_REGEX, main_window.lutFormatComboBox.currentText()
    )
    lut_format = lut_info_match.group("lut_format")
    lut_ext = lut_info_match.group("lut_ext")

    bake_cmd_data = {
        "ociobakelut_binary": "ociobakelut",
        "ocio_config": ["--iconfig", ocio_config],
        "input_space": ["--inputspace", input_space],
        "lut_format": ["--format", lut_format],
        "lut_ext": lut_ext,
    }

    if main_window.shaperColorSpacesCheckBox.checkState():
        bake_cmd_data["shaper_space"] = ["--shaperspace", shaper_space]
    if main_window.outputColorSpacesRadioButton.isChecked():
        bake_cmd_data["output_space"] = ["--outputspace", output_space]
    if main_window.looksRadioButton.isChecked():
        bake_cmd_data["looks"] = ["--looks", looks]
    if main_window.cubeSizeCheckBox.checkState():
        bake_cmd_data["cube_size"] = ["--cubesize", cube_size]
    if main_window.shaperSizeCheckBox.checkState():
        bake_cmd_data["shaper_size"] = ["--shapersize", shaper_size]

    if lut_ext == "icc":
        if main_window.iccWhitePointCheckBox.checkState():
            bake_cmd_data["icc_white_point"] = ["--whitepoint", icc_white_point]
        if main_window.iccDisplaysCheckBox.checkState():
            bake_cmd_data["icc_displays"] = ["--displayicc", icc_displays]
        if main_window.iccDescriptionCheckBox.checkState():
            bake_cmd_data["icc_description"] = ["--description", icc_description]
        if main_window.iccCopyrightCheckBox.checkState():
            bake_cmd_data["icc_copyright"] = ["--copyright", icc_copyright]

    bake_cmd_data["lut_filename"] = generate_lut_filename(main_window)

    return bake_cmd_data
