# pylint: disable=no-name-in-module
"""ui related submodule of the core module"""
import re
from dataclasses import dataclass
from typing import Any, Generator

from PySide2.QtCore import Qt, QSettings
from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication, QFileDialog, QMainWindow

from ocio_lut_prescription.core import ocio

LUT_INFO_REGEX = re.compile(r"^(?P<lut_format>\w+) \(.(?P<lut_ext>\w{3})\)$")
SIZES_LIST = [str(x) for x in range(1, 67)]


@dataclass
class BakeCmdData:  # pylint: disable=too-many-instance-attributes
    """Class keeping the content of the main window to be used when building the command line"""

    ociobakelut_bin: str
    ocio_config: str
    env_seq: str
    env_shot: str
    input_space: str
    use_shaper_space: bool
    shaper_space: str
    use_output_space: bool
    output_space: str
    use_looks: bool
    looks: str
    use_cube_size: bool
    cube_size: str
    use_shaper_size: bool
    shaper_size: str
    lut_format: str
    lut_ext: str
    use_icc_white_point: bool
    icc_white_point: str
    use_icc_displays: bool
    icc_displays: str
    use_icc_description: bool
    icc_description: str
    use_icc_copyright: bool
    icc_copyright: str
    output_dir: str
    use_override_lut_filename: bool
    override_lut_filename: str
    lut_filename: str


def load_ocio_config(main_window: QMainWindow, settings: QSettings):
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
    set_system_style(app, settings)
    initialize_ui_default(main_window)
    settings.clear()


def save_style_settings(settings: QSettings, style=None):
    settings.setValue("misc/style", style)
    settings.sync()


def save_settings(settings: QSettings, main_window: QMainWindow):
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
    palette = QPalette()
    app.setPalette(palette)
    save_style_settings(settings, style="system")


def browse_for_ocio_config(main_window: QMainWindow, settings: QSettings):
    ocio_config = QFileDialog.getOpenFileName(
        caption="Select OCIO Configuration", filter="*.ocio"
    )[0]
    main_window.ocioCfgLineEdit.setText(ocio_config)
    save_settings(settings, main_window)


def browse_for_lut_output_dir(main_window: QMainWindow, settings: QSettings):
    output_dir = QFileDialog.getExistingDirectory()
    main_window.outputDirLineEdit.setText(output_dir)
    check_to_enable_baking(main_window)
    save_settings(settings, main_window)


def check_to_enable_baking(main_window: QMainWindow):
    radio_check = any(
        [
            bool(main_window.outputColorSpacesRadioButton.isChecked()),
            bool(main_window.looksRadioButton.isChecked()),
        ]
    )
    output_check = bool(main_window.outputDirLineEdit.text())

    main_window.processBakeLutPushButton.setEnabled(all([radio_check, output_check]))


def initialize_ui_default(main_window: QMainWindow):
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


def get_bake_cmd_data(main_window: QMainWindow) -> tuple:
    lut_field = main_window.lutFormatComboBox.currentText()
    lut_info_match = re.match(LUT_INFO_REGEX, lut_field)

    return (
        "ociobakelut",
        main_window.ocioCfgLineEdit.text(),
        main_window.ocioSeqLineEdit.text(),
        main_window.ocioShotLineEdit.text(),
        main_window.inputColorSpacesComboBox.currentText(),
        main_window.shaperColorSpacesCheckBox.isChecked(),
        main_window.shaperColorSpacesComboBox.currentText(),
        main_window.outputColorSpacesRadioButton.isChecked(),
        main_window.outputColorSpacesComboBox.currentText(),
        main_window.looksRadioButton.isChecked(),
        main_window.looksComboBox.currentText(),
        main_window.cubeSizeCheckBox.isChecked(),
        main_window.cubeSizeComboBox.currentText(),
        main_window.shaperSizeCheckBox.isChecked(),
        main_window.shaperSizeComboBox.currentText(),
        lut_info_match.group("lut_format"),
        lut_info_match.group("lut_ext"),
        main_window.iccWhitePointCheckBox.isChecked(),
        main_window.iccWhitePointLineEdit.text(),
        main_window.iccDisplaysCheckBox.isChecked(),
        main_window.iccDisplaysComboBox.currentText(),
        main_window.iccDescriptionCheckBox.isChecked(),
        main_window.iccDescriptionLineEdit.text(),
        main_window.iccCopyrightCheckBox.isChecked(),
        main_window.iccCopyrightLineEdit.text(),
        main_window.outputDirLineEdit.text(),
        main_window.overrideLutNameCheckBox.isChecked(),
        main_window.overrideLutNameLineEdit.text(),
        "",
    )
