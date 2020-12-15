"""UI Wrapper script over the "ociobakelut" command

Icon Copyright:
Prescription by Dam from the Noun Project
"""
import re
from contextlib import contextmanager
from functools import wraps
import os
import signal
import subprocess
import sys
from typing import Generator

import PyOpenColorIO as OCIO

from PySide2.QtCore import Qt, QCoreApplication, QSettings
from PySide2.QtWidgets import QApplication, QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon, QPalette, QColor, QIntValidator

from ocioLutPrescription import ocioLutPrescription_qrc

SIZES_LIST = [str(x) for x in range(1, 67)]
LUT_INFO_REGEX = re.compile(r"^(?P<lut_format>\w+) \(.(?P<lut_ext>\w{3})\)$")


def _load_ocio_config(mainWindow, settings):
    """Load an ocio configuration

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`

    :raise OCIO.Exception: If the supplied ocio configuration
    """
    ocio_config_path = mainWindow.ocioCfgLineEdit.text()

    if ocio_config_path:
        try:
            ocio_config_obj = OCIO.Config.CreateFromFile(ocio_config_path)
        except OCIO.Exception as err:
            raise err

        if ocio_config_obj:
            initialize_ui_with_config_data(mainWindow, ocio_config_obj)
            save_settings(settings, mainWindow)


def _get_colorspaces_names_list(ocio_config_obj: OCIO.Config) -> Generator["Any", "Any", None]:
    """Retrieve the colorspace names from the OCIO configuration object
    """
    return (
        colorspace_name
        for colorspace_name
        in ocio_config_obj.getColorSpaceNames()
    )


def _get_looks_names_list(ocio_config_obj: OCIO.Config) -> Generator["Any", "Any", None]:
    """Retrieve the look names from the OCIO configuration object
    """
    return (
        look_name
        for look_name
        in ocio_config_obj.getLookNames()
    )


def _get_displays_list(ocio_config_obj: OCIO.Config) -> Generator["Any", "Any", None]:
    """Retrieve the display names from the OCIO configuration object
    """
    return (
        display
        for display
        in ocio_config_obj.getDisplays()
    )


def browse_for_ocio_config(mainWindow, settings):
    """Browse for ocio config, and saves settings

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    """
    ocio_config = QFileDialog.getOpenFileName(
        caption="Select OCIO Configuration",
        filter="*.ocio")[0]
    mainWindow.ocioCfgLineEdit.setText(ocio_config)
    save_settings(settings, mainWindow)


def browse_for_lut_output_dir(mainWindow, settings):
    """Browse for output directory, and saves settings

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    """
    output_dir = QFileDialog.getExistingDirectory()
    mainWindow.outputDirLineEdit.setText(output_dir)
    check_to_enable_baking(mainWindow)
    save_settings(settings, mainWindow)


def check_to_enable_baking(mainWindow):
    """Check if all command prerequesites are selected, to enable baking

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
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


def initialize_ui_default(mainWindow):
    """Initialize default UI state

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
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


def initialize_ui_with_config_data(mainWindow, ocioConfigObj):
    """Initialize UI state when a config is loaded

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param ocioConfigObj: the ocio configuration object
    :type ocioConfigObj: :class:`PyOpenColorIO.Config`
    """
    mainWindow.shaperColorSpacesCheckBox.setEnabled(True)
    mainWindow.outputColorSpacesRadioButton.setEnabled(True)
    mainWindow.looksRadioButton.setEnabled(True)

    mainWindow.inputColorSpacesComboBox.addItems(_get_colorspaces_names_list(ocioConfigObj))
    mainWindow.shaperColorSpacesComboBox.addItems(_get_colorspaces_names_list(ocioConfigObj))
    mainWindow.outputColorSpacesComboBox.addItems(_get_colorspaces_names_list(ocioConfigObj))
    mainWindow.looksComboBox.addItems(_get_looks_names_list(ocioConfigObj))
    mainWindow.iccDisplaysComboBox.addItems(_get_displays_list(ocioConfigObj))

    mainWindow.cubeSizeComboBox.setCurrentIndex(32)
    mainWindow.shaperSizeComboBox.setCurrentIndex(32)

    mainWindow.inputColorSpacesComboBox.setEnabled(True)
    mainWindow.outputColorSpacesRadioButton.setChecked(True)

    check_to_enable_baking(mainWindow)


def generate_lut_filename(mainWindow):
    """Generate the lut file name, use overriden name if available

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: The lut file name
    :rtype: str
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


def build_lut_radical(mainWindow):
    """build and return the automagic lut radical

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: the lut radical
    :rtype: str
    """
    return "_to_".join(
        [
            get_colorspace_input_prefix(mainWindow),
            get_lut_color_output_suffix(mainWindow)
        ]
    )


def get_colorspace_input_prefix(mainWindow):
    """build the lut radical colorspace input prefix from the UI

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: colorspace input prefix
    :rtype: str
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


def get_lut_color_output_suffix(mainWindow):
    """build the lut radical colorspace output suffix from the UI

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: colorspace output suffix
    :rtype: str
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


def get_bake_cmd_data(mainWindow):
    """From the mainWindow, get all the data needed to build an ociobakelut command

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: the data needed to build the command
    :rtype: dict
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


def get_ociobakelut_cmd(bake_cmd_data):
    """Build a valid ociobakelut command

    :param dict bake_cmd_data: the data needed to build the ociobakelut command

    :return: the ociobakelut command to be executed
    :rtype: list
    """
    cmd = ["ociobakelut"]
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


def ocio_report(bake_cmd_data, ociobakelut_cmd):
    """Basic report of the ociobakelut command

    :param dict bake_cmd_data: data used to make the command
    :param list ociobakelut_cmd: executed command

    :return: the log to be append to textEdit
    :rtype: str
    """
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


def settings_clear(app, settings, mainWindow):
    """Sets default Sytle/clear all the settings/restore default appearance

    :param app: the application
    :type app: :class:`PySide2.QtWidgets.QApplication`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    """
    set_system_style(app, settings)
    initialize_ui_default(mainWindow)
    settings.clear()


def save_style_settings(settings, style=None):
    """save only the style setting

    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    :param str style: the type of style (system|dark)
    """
    settings.setValue("misc/style", style)
    settings.sync()


def save_settings(settings, mainWindow):
    """save settings

    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
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


def load_settings(app, settings, mainWindow):
    """load applications settings

    :param app: the application
    :type app: :class:`PySide2.QtWidgets.QApplication`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
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
        ocio_config_obj = OCIO.Config.CreateFromFile(ocio_config_path)

        if ocio_config_obj:
            initialize_ui_with_config_data(mainWindow, ocio_config_obj)

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


def check_for_icc(mainWindow, lutFormatComboBoxText):
    """Enable ICC Options is icc format is selected

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param str lutFormatComboBoxText: the current text of the combo box
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


def set_dark_style(app, settings):
    """Sets custom dark style, and save

    :param app: the application
    :type app: :class:`PySide2.QtWidgets.QApplication`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
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


def set_system_style(app, settings):
    """Sets back the default system style, and save

    :param app: the application
    :type app: :class:`PySide2.QtWidgets.QApplication`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    """
    palette = QPalette()
    app.setPalette(palette)
    save_style_settings(settings, style="system")


def main():
    """main application function
    """
    # Adds Ctrl+C support to kill app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    env_ocio = os.environ.get("OCIO")
    env_sequence = os.environ.get("SEQ")
    env_shot = os.environ.get("SHOT")

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.setOrganizationName("djieffx")
    app.setApplicationName("ocioLutPrescription")

    loader = QUiLoader()
    mainWindow = loader.load(os.path.join(os.path.dirname(__file__), "ocioLutPrescription_mainWindow.ui"))
    mainWindow.setWindowIcon(QIcon(":/icons/ocioLutPrescription_icon.png"))
    mainWindow.iccWhitePointLineEdit.setValidator(QIntValidator(1, 10000))

    settings = QSettings()
    if env_ocio:
        mainWindow.ocioCfgLineEdit.setText(env_ocio)
        mainWindow.ocioSeqLineEdit.setText(env_sequence)
        mainWindow.ocioShotLineEdit.setText(env_shot)
        _load_ocio_config(mainWindow, settings)
    else:
        load_settings(app, settings, mainWindow)

    @contextmanager
    def ocio_context():
        """Keep current ocio context in memory, in case values are overriden in the UI
        """
        sequence_context = mainWindow.ocioSeqLineEdit.text()
        shot_context = mainWindow.ocioShotLineEdit.text()

        if sequence_context:
            os.environ["SEQ"] = sequence_context

        if shot_context:
            os.environ["SHOT"] = shot_context

        yield

        if sequence_context:
            if env_sequence is None:
                del os.environ["SEQ"]
            else:
                os.environ["SEQ"] = env_sequence

        if shot_context:
            if env_shot is None:
                del os.environ["SHOT"]
            else:
                os.environ["SHOT"] = env_shot

    def with_ocio_context():
        """decorator which allows running functions in an ocio context
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with ocio_context():
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    @with_ocio_context()
    def process_bake_lut():
        """from the UI, generate a valid ociobakelut command, and execute it
        """
        bake_cmd_data = get_bake_cmd_data(mainWindow)
        lut_result_file = bake_cmd_data["lut_filename"]
        ociobakelut_cmd = get_ociobakelut_cmd(bake_cmd_data)

        process = subprocess.Popen(ociobakelut_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode:
            mainWindow.resultLineEdit.setText("Error")
            mainWindow.resultLogTextEdit.setText(stderr.decode("utf-8"))
            print(" ".join(ociobakelut_cmd))
        else:
            mainWindow.resultLineEdit.setText(lut_result_file)
            stringedLog = ocio_report(bake_cmd_data, ociobakelut_cmd)
            mainWindow.resultLogTextEdit.setText(stringedLog)

    mainWindow.ocioCfgLoadPushButton.clicked.connect(
        lambda x: browse_for_ocio_config(mainWindow, settings)
    )
    mainWindow.outputDirBrowsePushButton.clicked.connect(
        lambda x: browse_for_lut_output_dir(mainWindow, settings)
    )
    mainWindow.ocioCfgLineEdit.textChanged.connect(
        lambda x: _load_ocio_config(mainWindow, settings)
    )
    mainWindow.outputDirLineEdit.textChanged.connect(
        lambda x: check_to_enable_baking(mainWindow)
    )
    mainWindow.outputDirLineEdit.textChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.inputColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.outputColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.shaperColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.looksComboBox.currentIndexChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.lutFormatComboBox.currentIndexChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.lutFormatComboBox.currentIndexChanged.connect(
        lambda x: check_for_icc(mainWindow, mainWindow.lutFormatComboBox.currentText())
    )
    mainWindow.cubeSizeComboBox.currentIndexChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.shaperSizeComboBox.currentIndexChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.iccWhitePointLineEdit.textChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.iccDisplaysComboBox.currentIndexChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.iccDescriptionLineEdit.textChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.iccCopyrightLineEdit.textChanged.connect(
        lambda x: save_settings(settings, mainWindow)
    )
    mainWindow.actionSetDarkStyle.triggered.connect(
        lambda x: set_dark_style(app, settings)
    )
    mainWindow.actionSetSystemStyle.triggered.connect(
        lambda x: set_system_style(app, settings)
    )
    mainWindow.actionSettingsClear.triggered.connect(
        lambda x: settings_clear(app, settings, mainWindow)
    )
    mainWindow.processBakeLutPushButton.clicked.connect(process_bake_lut)

    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
