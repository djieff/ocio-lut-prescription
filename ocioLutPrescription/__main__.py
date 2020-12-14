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
import PyOpenColorIO as OCIO

from PySide2.QtCore import Qt, QCoreApplication, QSettings
from PySide2.QtWidgets import QApplication, QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon, QPalette, QColor, QIntValidator

from ocioLutPrescription import ocioLutPrescription_qrc

SIZES_LIST = [str(x) for x in range(1, 67)]
LUT_INFO_REGEX = re.compile(r"^(?P<lutFormat>\w+) \(.(?P<lutExt>\w{3})\)$")


def _loadOCIOConfig(mainWindow, settings):
    """Load an ocio configuration

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`

    :raise OCIO.Exception: If the supplied ocio configuration
    """
    ocioConfigPath = mainWindow.ocioCfgLineEdit.text()

    if ocioConfigPath:
        try:
            ocioConfigObj = OCIO.Config.CreateFromFile(ocioConfigPath)
        except OCIO.Exception as err:
            raise err

        if ocioConfigObj:
            initializeUIWithConfigData(mainWindow, ocioConfigObj)
            saveSettings(settings, mainWindow)


def _getColorSpaceNamesList(ocioConfigObj):
    """Retrieve the colorspace names from the OCIO configuration object

    :param ocioConfigObj: the ocio configuration object
    :type ocioConfigObj: :class:`PyOpenColorIO.Config`

    :return: the list of colorspaces available
    """
    return (
        colorSpaceName
        for colorSpaceName
        in ocioConfigObj.getColorSpaceNames()
    )


def _getLookNamesList(ocioConfigObj):
    """Retrieve the look names from the OCIO configuration object

    :param ocioConfigObj: the ocio configuration object
    :type ocioConfigObj: :class:`PyOpenColorIO.Config`

    :return: the list of looks available
    """
    return (
        lookName
        for lookName
        in ocioConfigObj.getLookNames()
    )


def _getDisplaysList(ocioConfigObj):
    """Retrieve the display names from the OCIO configuration object

    :param ocioConfigObj: the ocio configuration object
    :type ocioConfigObj: :class:`PyOpenColorIO.Config`

    :return: the list of displays available
    """
    return (
        display
        for display
        in ocioConfigObj.getDisplays()
    )


def browseForOcioConfig(mainWindow, settings):
    """Browse for ocio config, and saves settings

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    """
    ocioConfig = QFileDialog.getOpenFileName(
        caption="Select OCIO Configuration",
        filter="*.ocio")[0]
    mainWindow.ocioCfgLineEdit.setText(ocioConfig)
    saveSettings(settings, mainWindow)


def browseForLutOutputDir(mainWindow, settings):
    """Browse for output directory, and saves settings

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    """
    outputDir = QFileDialog.getExistingDirectory()
    mainWindow.outputDirLineEdit.setText(outputDir)
    checkToEnableBaking(mainWindow)
    saveSettings(settings, mainWindow)


def checkToEnableBaking(mainWindow):
    """Check if all command prerequesites are selected, to enable baking

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    """
    radioCheck = any(
        [
            bool(mainWindow.outputColorSpacesRadioButton.isChecked()),
            bool(mainWindow.looksRadioButton.isChecked())
        ]
    )
    outputCheck = bool(mainWindow.outputDirLineEdit.text())

    mainWindow.processBakeLutPushButton.setEnabled(True) \
        if all([radioCheck, outputCheck]) \
        else mainWindow.processBakeLutPushButton.setDisabled(True)


def initializeUIDefault(mainWindow):
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


def initializeUIWithConfigData(mainWindow, ocioConfigObj):
    """Initialize UI state when a config is loaded

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    :param ocioConfigObj: the ocio configuration object
    :type ocioConfigObj: :class:`PyOpenColorIO.Config`
    """
    mainWindow.shaperColorSpacesCheckBox.setEnabled(True)
    mainWindow.outputColorSpacesRadioButton.setEnabled(True)
    mainWindow.looksRadioButton.setEnabled(True)

    mainWindow.inputColorSpacesComboBox.addItems(_getColorSpaceNamesList(ocioConfigObj))
    mainWindow.shaperColorSpacesComboBox.addItems(_getColorSpaceNamesList(ocioConfigObj))
    mainWindow.outputColorSpacesComboBox.addItems(_getColorSpaceNamesList(ocioConfigObj))
    mainWindow.looksComboBox.addItems(_getLookNamesList(ocioConfigObj))
    mainWindow.iccDisplaysComboBox.addItems(_getDisplaysList(ocioConfigObj))

    mainWindow.cubeSizeComboBox.setCurrentIndex(32)
    mainWindow.shaperSizeComboBox.setCurrentIndex(32)

    mainWindow.inputColorSpacesComboBox.setEnabled(True)
    mainWindow.outputColorSpacesRadioButton.setChecked(True)

    checkToEnableBaking(mainWindow)


def generateLutFileName(mainWindow):
    """Generate the lut file name, use overriden name if available

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: The lut file name
    :rtype: str
    """

    lutInfoMatch = re.match(LUT_INFO_REGEX, mainWindow.lutFormatComboBox.currentText())
    lutExt = lutInfoMatch.group("lutExt")
    outDir = mainWindow.outputDirLineEdit.text()

    lutRadical = (
        mainWindow.overrideLutNameLineEdit.text()
        if mainWindow.overrideLutNameCheckBox.isChecked() and mainWindow.overrideLutNameLineEdit.text()
        else buildLutRadical(mainWindow)
    )

    lutFileName = os.path.join(outDir, ".".join([lutRadical, lutExt]))

    return lutFileName


def buildLutRadical(mainWindow):
    """build and return the automagic lut radical

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: the lut radical
    :rtype: str
    """
    return "_to_".join(
        [
            getColorSpaceInputPrefix(mainWindow),
            getLutColorOutputSuffix(mainWindow)
        ]
    )


def getColorSpaceInputPrefix(mainWindow):
    """build the lut radical colorspace input prefix from the UI

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: colorspace input prefix
    :rtype: str
    """
    envPrefix = "".join(
        [
            "seq-{0}_".format(mainWindow.ocioSeqLineEdit.text())
            if mainWindow.ocioSeqLineEdit.text()
            else "",
            "shot-{0}_".format(mainWindow.ocioShotLineEdit.text())
            if mainWindow.ocioShotLineEdit.text()
            else "",
        ]
    )

    inputPrefix = mainWindow.inputColorSpacesComboBox.currentText().replace(" ", "_")

    shaperPrefix = "_shaper-{0}".format(
        mainWindow.shaperColorSpacesComboBox.currentText().replace(" ", "_")) \
        if mainWindow.shaperColorSpacesCheckBox.isChecked() \
        else ""

    return "".join(
        [
            envPrefix,
            inputPrefix,
            shaperPrefix
        ]
    )


def getLutColorOutputSuffix(mainWindow):
    """build the lut radical colorspace output suffix from the UI

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: colorspace output suffix
    :rtype: str
    """
    outputSuffix = mainWindow.outputColorSpacesComboBox.currentText().replace(" ", "_") + "_"\
        if mainWindow.outputColorSpacesComboBox.currentText() \
        else mainWindow.looksComboBox.currentText().replace(" ", "_")

    cubeSizeSuffix = "c{0}_".format(
        mainWindow.cubeSizeComboBox.currentText()) \
        if mainWindow.cubeSizeCheckBox.checkState() \
        else ""

    shaperSizeSuffix = "s{0}_".format(
        mainWindow.shaperSizeComboBox.currentText()) \
        if mainWindow.shaperSizeCheckBox.checkState() \
        else ""

    iccOnlySuffix = ""
    if mainWindow.lutFormatComboBox.currentText() == "icc (.icc)":
        iccOnlySuffix = "".join(
            [
                "D{0}_".format(mainWindow.iccWhitePointLineEdit.text())
                if mainWindow.iccWhitePointCheckBox.isChecked()
                else "",
                "displayICC-{0}_".format(mainWindow.iccDisplaysComboBox.currentText().replace(" ", "_"))
                if mainWindow.iccDisplaysCheckBox.isChecked()
                else ""
            ]
        )

    return "".join(
        [
            outputSuffix,
            cubeSizeSuffix,
            shaperSizeSuffix,
            iccOnlySuffix,
        ]
    ).rstrip("_")


def getBakeCmdData(mainWindow):
    """From the mainWindow, get all the data needed to build an ociobakelut command

    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`

    :return: the data needed to build the command
    :rtype: dict
    """
    ocioConfig = mainWindow.ocioCfgLineEdit.text()
    inputSpace = mainWindow.inputColorSpacesComboBox.currentText()
    shaperSpace = mainWindow.shaperColorSpacesComboBox.currentText()
    outputSpace = mainWindow.outputColorSpacesComboBox.currentText()
    looks = mainWindow.looksComboBox.currentText()
    cubeSize = mainWindow.cubeSizeComboBox.currentText()
    shaperSize = mainWindow.shaperSizeComboBox.currentText()
    iccWhitePoint = mainWindow.iccWhitePointLineEdit.text()
    iccDisplays = mainWindow.iccDisplaysComboBox.currentText()
    iccDescription = mainWindow.iccDescriptionLineEdit.text()
    iccCopyright = mainWindow.iccCopyrightLineEdit.text()

    lutInfoMatch = re.match(LUT_INFO_REGEX, mainWindow.lutFormatComboBox.currentText())
    lutFormat = lutInfoMatch.group("lutFormat")
    lutExt = lutInfoMatch.group("lutExt")

    bakeCmdData = {
        "iconfig": ["--iconfig", ocioConfig],
        "inputSpace": ["--inputspace", inputSpace],
        "lutFormat": ["--format", lutFormat],
        "lutExt": lutExt,
    }

    if mainWindow.shaperColorSpacesCheckBox.checkState():
        bakeCmdData["shaperSpace"] = ["--shaperspace", shaperSpace]
    if mainWindow.outputColorSpacesRadioButton.isChecked():
        bakeCmdData["outputSpace"] = ["--outputspace", outputSpace]
    if mainWindow.looksRadioButton.isChecked():
        bakeCmdData["looks"] = ["--looks", looks]
    if mainWindow.cubeSizeCheckBox.checkState():
        bakeCmdData["cubeSize"] = ["--cubesize", cubeSize]
    if mainWindow.shaperSizeCheckBox.checkState():
        bakeCmdData["shaperSize"] = ["--shapersize", shaperSize]

    if lutFormat == "icc":
        if mainWindow.iccWhitePointCheckBox.checkState():
            bakeCmdData["iccWhitePoint"] = ["--whitepoint", iccWhitePoint]
        if mainWindow.iccDisplaysCheckBox.checkState():
            bakeCmdData["iccDisplays"] = ["--displayicc", iccDisplays]
        if mainWindow.iccDescriptionCheckBox.checkState():
            bakeCmdData["iccDescription"] = ["--description", iccDescription]
        if mainWindow.iccCopyrightCheckBox.checkState():
            bakeCmdData["iccCopyright"] = ["--copyright", iccCopyright]

    bakeCmdData["lutFileName"] = generateLutFileName(mainWindow)

    return bakeCmdData


def getOcioBakeLutCmd(bakeCmdData):
    """Build a valid ociobakelut command

    :param dict bakeCmdData: the data needed to build the ociobakelut command

    :return: the ociobakelut command to be executed
    :rtype: list
    """
    cmd = ["ociobakelut"]
    cmd.extend(bakeCmdData["iconfig"])
    cmd.extend(bakeCmdData["inputSpace"])
    cmd.extend(bakeCmdData.get("shaperSpace", ""))
    cmd.extend(bakeCmdData.get("outputSpace", bakeCmdData.get("looks")))
    cmd.extend(bakeCmdData["lutFormat"])
    cmd.extend(bakeCmdData.get("cubeSize", ""))
    cmd.extend(bakeCmdData.get("shaperSize", ""))

    if bakeCmdData["lutFormat"] == "icc":
        cmd.extend(bakeCmdData.get("iccWhitePoint", ""))
        cmd.extend(bakeCmdData.get("iccDisplays", ""))
        cmd.extend(bakeCmdData.get("iccDescription", ""))
        cmd.extend(bakeCmdData.get("iccCopyright", ""))

    cmd.append(bakeCmdData["lutFileName"])

    return cmd


def ocioReport(bakeCmdData, ocioBakeLutCmd):
    """Basic report of the ociobakelut command

    :param dict bakeCmdData: data used to make the command
    :param list ocioBakeLutCmd: executed command

    :return: the log to be append to textEdit
    :rtype: str
    """
    return (
        "--------- LUT prescription below -----------\n"
        "\n"
        "OCIO: {0}\n"
        "SEQ: {1}\n"
        "SHOT: {2}\n"
        "Input ColorSpace: {3}\n"
        "Shaper ColorSpace: {4}\n"
        "Output ColorSpace: {5}\n"
        "Look: {6}\n"
        "\n"
        "LUT Location: {7}\n"
        "\n"
        "Executed BakeLut Command: {8}\n"
        "\n"
        "--------------------------------------------".format(
            bakeCmdData["iconfig"][1],
            os.environ.get("SEQ", "N/A"),
            os.environ.get("SHOT", "N/A"),
            bakeCmdData["inputSpace"][1],
            bakeCmdData.get("shaperSpace", ["", "N/A"])[1],
            bakeCmdData.get("outputSpace", ["", "N/A"])[1],
            bakeCmdData.get("looks", ["", "N/A"])[1],
            bakeCmdData["lutFileName"],
            " ".join(ocioBakeLutCmd),
        )
    )


def settingsClear(app, settings, mainWindow):
    """Sets default Sytle/clear all the settings/restore default appearance

    :param app: the application
    :type app: :class:`PySide2.QtWidgets.QApplication`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    """
    setSystemStyle(app, settings)
    initializeUIDefault(mainWindow)
    settings.clear()


def saveStyleSettings(settings, style=None):
    """save only the style setting

    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    :param str style: the type of style (system|dark)
    """
    settings.setValue("misc/style", style)
    settings.sync()


def saveSettings(settings, mainWindow):
    """save settings

    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    """
    settings.setValue("ocio/configPath", mainWindow.ocioCfgLineEdit.text())
    settings.setValue("colorspaces/input", mainWindow.inputColorSpacesComboBox.currentText())
    settings.setValue("colorspaces/shaper", mainWindow.shaperColorSpacesComboBox.currentText())
    settings.setValue("colorspaces/output", mainWindow.outputColorSpacesComboBox.currentText())
    settings.setValue("colorspaces/looks", mainWindow.looksComboBox.currentText())
    settings.setValue("output/directory", mainWindow.outputDirLineEdit.text())
    settings.setValue("baking/lutFormat", mainWindow.lutFormatComboBox.currentText())
    settings.setValue("baking/cubeSize", mainWindow.cubeSizeComboBox.currentText())
    settings.setValue("baking/shaperSize", mainWindow.shaperSizeComboBox.currentText())
    settings.setValue("icc/whitePoint", mainWindow.iccWhitePointLineEdit.text())
    settings.setValue("icc/displays", mainWindow.iccDisplaysComboBox.currentText())
    settings.setValue("icc/description", mainWindow.iccDescriptionLineEdit.text())
    settings.setValue("icc/copyright", mainWindow.iccCopyrightLineEdit.text())
    settings.sync()


def loadSettings(app, settings, mainWindow):
    """load applications settings

    :param app: the application
    :type app: :class:`PySide2.QtWidgets.QApplication`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    :param mainWindow: the application main window
    :type mainWindow: :class:`PySide2.QtWidgets.QMainWindow`
    """
    if settings.value("misc/style") == "dark":
        setDarkStyle(app, settings)

    ocioConfigPath = settings.value("ocio/configPath")
    if not ocioConfigPath:
        initializeUIDefault(mainWindow)
    else:
        mainWindow.ocioCfgLineEdit.setText(ocioConfigPath)
        ocioConfigObj = OCIO.Config.CreateFromFile(ocioConfigPath)

        if ocioConfigObj:
            initializeUIWithConfigData(mainWindow, ocioConfigObj)

            index = mainWindow.inputColorSpacesComboBox.findText(
                settings.value("colorspaces/input"), Qt.MatchFixedString
            )
            if index >= 0:
                mainWindow.inputColorSpacesComboBox.setCurrentIndex(index)

            index = mainWindow.shaperColorSpacesComboBox.findText(
                settings.value("colorspaces/shaper"), Qt.MatchFixedString
            )
            if index >= 0:
                mainWindow.shaperColorSpacesComboBox.setCurrentIndex(index)

            index = mainWindow.outputColorSpacesComboBox.findText(
                settings.value("colorspaces/output"), Qt.MatchFixedString
            )
            if index >= 0:
                mainWindow.outputColorSpacesComboBox.setCurrentIndex(index)

            index = mainWindow.looksComboBox.findText(
                settings.value("colorspaces/looks"), Qt.MatchFixedString
            )
            if index >= 0:
                mainWindow.looksComboBox.setCurrentIndex(index)

            mainWindow.outputDirLineEdit.setText(settings.value("output/directory"))

            index = mainWindow.lutFormatComboBox.findText(
                settings.value("baking/lutFormat"), Qt.MatchFixedString
            )
            if index >= 0:
                mainWindow.lutFormatComboBox.setCurrentIndex(index)

            mainWindow.cubeSizeComboBox.addItems(SIZES_LIST)

            index = mainWindow.cubeSizeComboBox.findText(
                settings.value("baking/cubeSize"), Qt.MatchFixedString
            )
            if index >= 0:
                mainWindow.cubeSizeComboBox.setCurrentIndex(index)

            mainWindow.cubeSizeComboBox.setDisabled(True)

            mainWindow.shaperSizeComboBox.addItems(SIZES_LIST)

            index = mainWindow.shaperSizeComboBox.findText(
                settings.value("baking/shaperSize"), Qt.MatchFixedString
            )
            if index >= 0:
                mainWindow.shaperSizeComboBox.setCurrentIndex(index)
            mainWindow.shaperSizeComboBox.setDisabled(True)

            mainWindow.iccWhitePointLineEdit.setText(settings.value("icc/whitePoint"))

            index = mainWindow.iccDisplaysComboBox.findText(
                settings.value("icc/displays"), Qt.MatchFixedString
            )
            if index >= 0:
                mainWindow.iccDisplaysComboBox.setCurrentIndex(index)

            mainWindow.iccDescriptionLineEdit.setText(settings.value("icc/description"))

            mainWindow.iccCopyrightLineEdit.setText(settings.value("icc/copyright"))
            mainWindow.outputDirLineEdit.setText(settings.value("output/directory"))

            checkForICC(mainWindow, mainWindow.lutFormatComboBox.currentText())
            checkToEnableBaking(mainWindow)


def checkForICC(mainWindow, lutFormatComboBoxText):
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


def setDarkStyle(app, settings):
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
    saveStyleSettings(settings, style="dark")


def setSystemStyle(app, settings):
    """Sets back the default system style, and save

    :param app: the application
    :type app: :class:`PySide2.QtWidgets.QApplication`
    :param settings: the application settings
    :type settings: :class:`PySide2.QtCore.QSettings`
    """
    palette = QPalette()
    app.setPalette(palette)
    saveStyleSettings(settings, style="system")


def main():
    """main application function
    """
    # Adds Ctrl+C support to kill app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    envOCIO = os.environ.get("OCIO")
    envSEQ = os.environ.get("SEQ")
    envSHOT = os.environ.get("SHOT")

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.setOrganizationName("djieffx")
    app.setApplicationName("ocioLutPrescription")

    loader = QUiLoader()
    mainWindow = loader.load(os.path.join(os.path.dirname(__file__), "ocioLutPrescription_mainWindow.ui"))
    mainWindow.setWindowIcon(QIcon(":/icons/ocioLutPrescription_icon.png"))
    mainWindow.iccWhitePointLineEdit.setValidator(QIntValidator(1, 10000))

    settings = QSettings()
    if envOCIO:
        mainWindow.ocioCfgLineEdit.setText(envOCIO)
        mainWindow.ocioSeqLineEdit.setText(envSEQ)
        mainWindow.ocioShotLineEdit.setText(envSHOT)
        _loadOCIOConfig(mainWindow, settings)
    else:
        loadSettings(app, settings, mainWindow)

    @contextmanager
    def ocioContext():
        """Keep current ocio context in memory, in case values are overriden in the UI
        """
        seqContext = mainWindow.ocioSeqLineEdit.text()
        shotContext = mainWindow.ocioShotLineEdit.text()

        if seqContext:
            os.environ["SEQ"] = seqContext

        if shotContext:
            os.environ["SHOT"] = shotContext

        yield

        if seqContext:
            if envSEQ is None:
                del os.environ["SEQ"]
            else:
                os.environ["SEQ"] = envSEQ

        if shotContext:
            if envSHOT is None:
                del os.environ["SHOT"]
            else:
                os.environ["SHOT"] = envSHOT

    def withOCIOContext():
        """decorator which allows running functions in an ocio context
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with ocioContext():
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    @withOCIOContext()
    def processBakeLut():
        """from the UI, generate a valid ociobakelut command, and execute it
        """
        bakeCmdData = getBakeCmdData(mainWindow)
        lutResultFile = bakeCmdData["lutFileName"]
        ocioBakeLutCmd = getOcioBakeLutCmd(bakeCmdData)

        process = subprocess.Popen(ocioBakeLutCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode:
            mainWindow.resultLineEdit.setText("Error")
            mainWindow.resultLogTextEdit.setText(stderr.decode("utf-8"))
            print(" ".join(ocioBakeLutCmd))
        else:
            mainWindow.resultLineEdit.setText(lutResultFile)
            stringedLog = ocioReport(bakeCmdData, ocioBakeLutCmd)
            mainWindow.resultLogTextEdit.setText(stringedLog)

    mainWindow.ocioCfgLoadPushButton.clicked.connect(
        lambda x: browseForOcioConfig(mainWindow, settings)
    )
    mainWindow.outputDirBrowsePushButton.clicked.connect(
        lambda x: browseForLutOutputDir(mainWindow, settings)
    )
    mainWindow.ocioCfgLineEdit.textChanged.connect(
        lambda x: _loadOCIOConfig(mainWindow, settings)
    )
    mainWindow.outputDirLineEdit.textChanged.connect(
        lambda x: checkToEnableBaking(mainWindow)
    )
    mainWindow.outputDirLineEdit.textChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.inputColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.outputColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.shaperColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.looksComboBox.currentIndexChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.lutFormatComboBox.currentIndexChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.lutFormatComboBox.currentIndexChanged.connect(
        lambda x: checkForICC(mainWindow, mainWindow.lutFormatComboBox.currentText())
    )
    mainWindow.cubeSizeComboBox.currentIndexChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.shaperSizeComboBox.currentIndexChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.iccWhitePointLineEdit.textChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.iccDisplaysComboBox.currentIndexChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.iccDescriptionLineEdit.textChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.iccCopyrightLineEdit.textChanged.connect(
        lambda x: saveSettings(settings, mainWindow)
    )
    mainWindow.actionSetDarkStyle.triggered.connect(
        lambda x: setDarkStyle(app, settings)
    )
    mainWindow.actionSetSystemStyle.triggered.connect(
        lambda x: setSystemStyle(app, settings)
    )
    mainWindow.actionSettingsClear.triggered.connect(
        lambda x: settingsClear(app, settings, mainWindow)
    )
    mainWindow.processBakeLutPushButton.clicked.connect(processBakeLut)

    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
