
import os
import re
from typing import Generator

from ocioLutPrescription.olp_modules import ocio

from PySide2.QtCore import Qt, QSettings
from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication, QFileDialog, QMainWindow

LUT_INFO_REGEX = re.compile(r"^(?P<lut_format>\w+) \(.(?P<lut_ext>\w{3})\)$")
SIZES_LIST = [str(x) for x in range(1, 67)]


def load_ocio_config(mainWindow: QMainWindow, settings: QSettings):
    """
    """
    ocio_config_path = mainWindow.ocioCfgLineEdit.text()

    if ocio_config_path:
        ocio_config_obj = ocio.create_ocio_config_object(ocio_config_path)

        input_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        shaper_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        output_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
        looks_generator = ocio.get_looks_names_list(ocio_config_obj)
        displays_generator = ocio.get_displays_list(ocio_config_obj)

        if ocio_config_obj:
            initialize_ui_with_config_data(
                mainWindow,
                input_colorspaces_generator,
                shaper_colorspaces_generator,
                output_colorspaces_generator,
                looks_generator,
                displays_generator
            )
            save_settings(settings, mainWindow)


def settings_clear(app: QApplication, settings: QSettings, mainWindow: QMainWindow):
    """
    """
    set_system_style(app, settings)
    initialize_ui_default(mainWindow)
    settings.clear()


def save_style_settings(settings: QSettings, style=None):
    """
    """
    settings.setValue("misc/style", style)
    settings.sync()


def save_settings(settings: QSettings, mainWindow: QMainWindow):
    """
    """
    settings.setValue("ocio/config_path", mainWindow.ocioCfgLineEdit.text())
    settings.setValue("colorspaces/input", mainWindow.inputColorSpacesComboBox.currentText())
    settings.setValue("colorspaces/shaper", mainWindow.shaperColorSpacesComboBox.currentText())
    settings.setValue("colorspaces/output", mainWindow.outputColorSpacesComboBox.currentText())
    settings.setValue("colorspaces/looks", mainWindow.looksComboBox.currentText())
    settings.setValue("output/directory", mainWindow.outputDirLineEdit.text())
    settings.setValue("baking/lut_format", mainWindow.lutFormatComboBox.currentText())
    settings.setValue("baking/cube_size", mainWindow.cubeSizeComboBox.currentText())
    settings.setValue("baking/shaper_size", mainWindow.shaperSizeComboBox.currentText())
    settings.setValue("icc/white_point", mainWindow.iccWhitePointLineEdit.text())
    settings.setValue("icc/displays", mainWindow.iccDisplaysComboBox.currentText())
    settings.setValue("icc/description", mainWindow.iccDescriptionLineEdit.text())
    settings.setValue("icc/copyright", mainWindow.iccCopyrightLineEdit.text())
    settings.sync()


def load_settings(app: QApplication, settings: QSettings, mainWindow: QMainWindow):
    """
    """
    combo_box_settings = {
        mainWindow.inputColorSpacesComboBox: "colorspaces/input",
        mainWindow.shaperColorSpacesComboBox: "colorspaces/shaper",
        mainWindow.outputColorSpacesComboBox: "colorspaces/output",
        mainWindow.looksComboBox: "colorspaces/looks",
        mainWindow.lutFormatComboBox: "baking/lut_format",
        mainWindow.cubeSizeComboBox: "baking/cube_size",
        mainWindow.shaperSizeComboBox: "baking/shaper_size",
        mainWindow.iccDisplaysComboBox: "icc/displays",
    }
    line_edit_settings = {
        mainWindow.iccWhitePointLineEdit: "icc/white_point",
        mainWindow.iccDescriptionLineEdit: "icc/description",
        mainWindow.iccCopyrightLineEdit: "icc/copyright",
        mainWindow.outputDirLineEdit: "output/directory"
    }

    if settings.value("misc/style") == "dark":
        set_dark_style(app, settings)

    ocio_config_path = settings.value("ocio/config_path")
    if not ocio_config_path:
        initialize_ui_default(mainWindow)
    else:
        mainWindow.ocioCfgLineEdit.setText(ocio_config_path)
        ocio_config_obj = ocio.create_ocio_config_object(ocio_config_path)

        if ocio_config_obj:
            input_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
            shaper_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
            output_colorspaces_generator = ocio.get_colorspaces_names_list(ocio_config_obj)
            looks_generator = ocio.get_looks_names_list(ocio_config_obj)
            displays_generator = ocio.get_displays_list(ocio_config_obj)

            initialize_ui_with_config_data(
                mainWindow,
                input_colorspaces_generator,
                shaper_colorspaces_generator,
                output_colorspaces_generator,
                looks_generator,
                displays_generator
            )

            mainWindow.cubeSizeComboBox.addItems(SIZES_LIST)
            mainWindow.cubeSizeComboBox.setDisabled(True)
            mainWindow.shaperSizeComboBox.addItems(SIZES_LIST)
            mainWindow.shaperSizeComboBox.setDisabled(True)

            for widget, combobox_setting in combo_box_settings.items():
                index = widget.findText(settings.value(combobox_setting), Qt.MatchFixedString)
                if index >= 0:
                    widget.setCurrentIndex(index)

            for widget, lineedit_setting in line_edit_settings.items():
                widget.setText(settings.value(lineedit_setting))

            check_for_icc(mainWindow, mainWindow.lutFormatComboBox.currentText())
            check_to_enable_baking(mainWindow)


def check_for_icc(mainWindow: QMainWindow, lutFormatComboBoxText: str):
    """Enable ICC Options is icc format is selected
    """
    if "icc" in lutFormatComboBoxText:
        mainWindow.iccWhitePointCheckBox.setEnabled(True)
        mainWindow.iccDisplaysCheckBox.setEnabled(True)
        mainWindow.iccDescriptionCheckBox.setEnabled(True)
        mainWindow.iccCopyrightCheckBox.setEnabled(True)

        if mainWindow.iccWhitePointCheckBox.isChecked():
            mainWindow.iccWhitePointLineEdit.setEnabled(True)

        if mainWindow.iccDisplaysCheckBox.isChecked():
            mainWindow.iccDisplaysComboBox.setEnabled(True)

        if mainWindow.iccDescriptionCheckBox.isChecked():
            mainWindow.iccDescriptionLineEdit.setEnabled(True)

        if mainWindow.iccCopyrightCheckBox.isChecked():
            mainWindow.iccCopyrightLineEdit.setEnabled(True)

    else:
        mainWindow.iccWhitePointCheckBox.setDisabled(True)
        mainWindow.iccDisplaysCheckBox.setDisabled(True)
        mainWindow.iccDescriptionCheckBox.setDisabled(True)
        mainWindow.iccCopyrightCheckBox.setDisabled(True)

        mainWindow.iccWhitePointLineEdit.setDisabled(True)
        mainWindow.iccDisplaysComboBox.setDisabled(True)
        mainWindow.iccDescriptionLineEdit.setDisabled(True)
        mainWindow.iccCopyrightLineEdit.setDisabled(True)


def set_dark_style(app: QApplication, settings: QSettings):
    """
    """
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
    """
    """
    palette = QPalette()
    app.setPalette(palette)
    save_style_settings(settings, style="system")


def browse_for_ocio_config(mainWindow: QMainWindow, settings: QSettings):
    """
    """
    ocio_config = QFileDialog.getOpenFileName(
        caption="Select OCIO Configuration",
        filter="*.ocio")[0]
    mainWindow.ocioCfgLineEdit.setText(ocio_config)
    save_settings(settings, mainWindow)


def browse_for_lut_output_dir(mainWindow: QMainWindow, settings: QSettings):
    """
    """
    output_dir = QFileDialog.getExistingDirectory()
    mainWindow.outputDirLineEdit.setText(output_dir)
    check_to_enable_baking(mainWindow)
    save_settings(settings, mainWindow)


def check_to_enable_baking(mainWindow: QMainWindow):
    """
    """
    radio_check = any(
        [
            bool(mainWindow.outputColorSpacesRadioButton.isChecked()),
            bool(mainWindow.looksRadioButton.isChecked())
        ]
    )
    output_check = bool(mainWindow.outputDirLineEdit.text())

    mainWindow.processBakeLutPushButton.setEnabled(True) \
        if all([radio_check, output_check]) \
        else mainWindow.processBakeLutPushButton.setDisabled(True)


def initialize_ui_default(mainWindow: QMainWindow):
    """
    """
    mainWindow.cubeSizeComboBox.clear()
    mainWindow.shaperSizeComboBox.clear()
    mainWindow.cubeSizeComboBox.addItems(SIZES_LIST)
    mainWindow.shaperSizeComboBox.addItems(SIZES_LIST)

    mainWindow.cubeSizeComboBox.setCurrentIndex(32)
    mainWindow.shaperSizeComboBox.setCurrentIndex(32)
    mainWindow.lutFormatComboBox.setCurrentIndex(0)

    mainWindow.inputColorSpacesComboBox.clear()
    mainWindow.shaperColorSpacesComboBox.clear()
    mainWindow.outputColorSpacesComboBox.clear()
    mainWindow.looksComboBox.clear()
    mainWindow.iccDisplaysComboBox.clear()
    mainWindow.ocioCfgLineEdit.clear()
    mainWindow.resultLineEdit.clear()
    mainWindow.resultLogTextEdit.clear()
    mainWindow.overrideLutNameLineEdit.clear()
    mainWindow.iccWhitePointLineEdit.clear()
    mainWindow.iccDescriptionLineEdit.clear()
    mainWindow.iccCopyrightLineEdit.clear()
    mainWindow.outputDirLineEdit.clear()

    mainWindow.processBakeLutPushButton.setDisabled(True)
    mainWindow.overrideLutNameCheckBox.setChecked(False)
    mainWindow.cubeSizeCheckBox.setChecked(False)
    mainWindow.shaperSizeCheckBox.setChecked(False)
    mainWindow.iccWhitePointCheckBox.setChecked(False)
    mainWindow.iccDisplaysCheckBox.setChecked(False)
    mainWindow.iccDescriptionCheckBox.setChecked(False)
    mainWindow.iccCopyrightCheckBox.setChecked(False)


def initialize_ui_with_config_data(
        mainWindow: QMainWindow,
        input_colorspaces_generator: Generator["Any", "Any", None],
        shaper_colorspaces_generator: Generator["Any", "Any", None],
        output_colorspaces_generator: Generator["Any", "Any", None],
        looks_generator: Generator["Any", "Any", None],
        displays_generator: Generator["Any", "Any", None]
        ):
    """
    """
    mainWindow.shaperColorSpacesCheckBox.setEnabled(True)
    mainWindow.outputColorSpacesRadioButton.setEnabled(True)
    mainWindow.looksRadioButton.setEnabled(True)

    mainWindow.inputColorSpacesComboBox.addItems(input_colorspaces_generator)
    mainWindow.shaperColorSpacesComboBox.addItems(shaper_colorspaces_generator)
    mainWindow.outputColorSpacesComboBox.addItems(output_colorspaces_generator)
    mainWindow.looksComboBox.addItems(looks_generator)
    mainWindow.iccDisplaysComboBox.addItems(displays_generator)

    mainWindow.cubeSizeComboBox.setCurrentIndex(32)
    mainWindow.shaperSizeComboBox.setCurrentIndex(32)

    mainWindow.inputColorSpacesComboBox.setEnabled(True)
    mainWindow.outputColorSpacesRadioButton.setChecked(True)

    check_to_enable_baking(mainWindow)


def generate_lut_filename(mainWindow: QMainWindow) -> str:
    """
    """
    lut_info_match = re.match(LUT_INFO_REGEX, mainWindow.lutFormatComboBox.currentText())
    lut_ext = lut_info_match.group("lut_ext")
    output_dir = mainWindow.outputDirLineEdit.text()

    lut_radical = (
        mainWindow.overrideLutNameLineEdit.text()
        if mainWindow.overrideLutNameCheckBox.isChecked() and mainWindow.overrideLutNameLineEdit.text()
        else build_lut_radical(mainWindow)
    )

    lut_filename = os.path.join(output_dir, ".".join([lut_radical, lut_ext]))

    return lut_filename


def build_lut_radical(mainWindow: QMainWindow) -> str:
    """
    """
    return "_to_".join(
        [
            get_colorspace_input_prefix(mainWindow),
            get_lut_color_output_suffix(mainWindow)
        ]
    )


def get_colorspace_input_prefix(mainWindow: QMainWindow) -> str:
    """
    """
    env_prefix = "".join(
        [
            f"seq-{mainWindow.ocioSeqLineEdit.text()}_"
            if mainWindow.ocioSeqLineEdit.text()
            else "",
            f"shot-{mainWindow.ocioShotLineEdit.text()}_"
            if mainWindow.ocioShotLineEdit.text()
            else "",
        ]
    )

    input_prefix = mainWindow.inputColorSpacesComboBox.currentText().replace(" ", "_")

    shaper_prefix = f"_shaper-{mainWindow.shaperColorSpacesComboBox.currentText().replace(' ', '_')}"\
        if mainWindow.shaperColorSpacesCheckBox.isChecked() \
        else ""

    return "".join(
        [
            env_prefix,
            input_prefix,
            shaper_prefix
        ]
    )


def get_lut_color_output_suffix(mainWindow: QMainWindow) -> str:
    """
    """
    output_suffix = mainWindow.outputColorSpacesComboBox.currentText().replace(" ", "_") + "_"\
        if mainWindow.outputColorSpacesComboBox.currentText() \
        else mainWindow.looksComboBox.currentText().replace(" ", "_")

    cube_size_suffix = f"c{mainWindow.cubeSizeComboBox.currentText()}_"\
        if mainWindow.cubeSizeCheckBox.checkState() \
        else ""

    shaper_size_suffix = f"s{mainWindow.shaperSizeComboBox.currentText()}_"\
        if mainWindow.shaperSizeCheckBox.checkState() \
        else ""

    icc_only_suffix = ""
    if mainWindow.lutFormatComboBox.currentText() == "icc (.icc)":
        icc_only_suffix = "".join(
            [
                f"D{mainWindow.iccWhitePointLineEdit.text()}_"
                if mainWindow.iccWhitePointCheckBox.isChecked()
                else "",
                f"displayICC-{mainWindow.iccDisplaysComboBox.currentText().replace(' ', '_')}_"
                if mainWindow.iccDisplaysCheckBox.isChecked()
                else ""
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


def get_bake_cmd_data(mainWindow: QMainWindow) -> dict:
    """
    """
    ocio_config = mainWindow.ocioCfgLineEdit.text()
    input_space = mainWindow.inputColorSpacesComboBox.currentText()
    shaper_space = mainWindow.shaperColorSpacesComboBox.currentText()
    output_space = mainWindow.outputColorSpacesComboBox.currentText()
    looks = mainWindow.looksComboBox.currentText()
    cube_size = mainWindow.cubeSizeComboBox.currentText()
    shaper_size = mainWindow.shaperSizeComboBox.currentText()
    icc_white_point = mainWindow.iccWhitePointLineEdit.text()
    icc_displays = mainWindow.iccDisplaysComboBox.currentText()
    icc_description = mainWindow.iccDescriptionLineEdit.text()
    icc_copyright = mainWindow.iccCopyrightLineEdit.text()

    lut_info_match = re.match(LUT_INFO_REGEX, mainWindow.lutFormatComboBox.currentText())
    lut_format = lut_info_match.group("lut_format")
    lut_ext = lut_info_match.group("lut_ext")

    bake_cmd_data = {
        "ocio_config": ["--iconfig", ocio_config],
        "input_space": ["--inputspace", input_space],
        "lut_format": ["--format", lut_format],
        "lut_ext": lut_ext,
    }

    if mainWindow.shaperColorSpacesCheckBox.checkState():
        bake_cmd_data["shaper_space"] = ["--shaperspace", shaper_space]
    if mainWindow.outputColorSpacesRadioButton.isChecked():
        bake_cmd_data["output_space"] = ["--outputspace", output_space]
    if mainWindow.looksRadioButton.isChecked():
        bake_cmd_data["looks"] = ["--looks", looks]
    if mainWindow.cubeSizeCheckBox.checkState():
        bake_cmd_data["cube_size"] = ["--cubesize", cube_size]
    if mainWindow.shaperSizeCheckBox.checkState():
        bake_cmd_data["shaper_size"] = ["--shapersize", shaper_size]

    if lut_format == "icc":
        if mainWindow.iccWhitePointCheckBox.checkState():
            bake_cmd_data["icc_white_point"] = ["--whitepoint", icc_white_point]
        if mainWindow.iccDisplaysCheckBox.checkState():
            bake_cmd_data["icc_displays"] = ["--displayicc", icc_displays]
        if mainWindow.iccDescriptionCheckBox.checkState():
            bake_cmd_data["icc_description"] = ["--description", icc_description]
        if mainWindow.iccCopyrightCheckBox.checkState():
            bake_cmd_data["icc_copyright"] = ["--copyright", icc_copyright]

    bake_cmd_data["lut_filename"] = generate_lut_filename(mainWindow)

    return bake_cmd_data
