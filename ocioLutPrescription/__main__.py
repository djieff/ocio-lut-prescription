"""UI Wrapper script over the "ociobakelut" command
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
from PySide2.QtGui import QIcon

from . import ocioLutPrescription_qrc


SIZES_LIST = [str(x) for x in range(1, 67)]

LUT_FORMATS = [
    "cinespace (.csp)",
    "flame (.3dl)",
    "houdini (.lut)",
    "icc (.icc)",
    "iridas_itx (.itx)",
    "lustre (.3dl)",
    "truelight (.cub)"
]

LUT_INFO_REGEX = re.compile(r"^(?P<lutFormat>\w+) \(.(?P<lutExt>\w{3})\)$")


def loadOCIOConfig(mainWindow):
    """
    """
    ocioConfigPath = mainWindow.ocioCfgLineEdit.text()
    ocioConfigData = extractOCIOConfigData(ocioConfigPath)

    if ocioConfigData:
        initializeUIWithConfigData(mainWindow, ocioConfigData)


def _getColorSpaceNamesList(ocioConfigObj):
    """
    """
    return [
        colorSpaceName
        for colorSpaceName
        in ocioConfigObj.getColorSpaceNames()
    ]


def _getLookNamesList(ocioConfigObj):
    """
    """
    return [
        lookName
        for lookName
        in ocioConfigObj.getLookNames()
    ]


def _getDisplaysList(ocioConfigObj):
    """
    """
    return [
        display
        for display
        in ocioConfigObj.getDisplays()
    ]


def browseForOcioConfig(mainWindow):
    """
    """
    ocioConfig = QFileDialog.getOpenFileName(
        caption="Select OCIO Configuration",
        filter="*.ocio")[0]
    mainWindow.ocioCfgLineEdit.setText(ocioConfig)


def browseForLutOutputDir(mainWindow):
    """
    """
    outputDir = QFileDialog.getExistingDirectory()
    mainWindow.outputDirLineEdit.setText(outputDir)
    checkToEnableBaking(mainWindow)


def checkToEnableBaking(mainWindow):
    """
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


def extractOCIOConfigData(ocioConfigPath):
    """extract data from ocio configuration

    :param str ocioConfigPath: path the ocio configuration

    :return: data from the ocio configuration
    :rtype: dict
    """
    ocioConfigObj = OCIO.Config.CreateFromFile(ocioConfigPath)

    ocioColorSpaces = _getColorSpaceNamesList(ocioConfigObj)
    ocioLooks = _getLookNamesList(ocioConfigObj)
    ocioDisplays = _getDisplaysList(ocioConfigObj)

    ocioConfigData = {
        "ocioColorSpaces": ocioColorSpaces,
        "ocioLooks": ocioLooks,
        "ocioDisplays": ocioDisplays
    }

    return ocioConfigData


def initializeUIDefault(mainWindow):
    """
    """
    mainWindow.inputColorSpacesComboBox.setDisabled(True)
    mainWindow.shaperColorSpacesCheckBox.setDisabled(True)
    mainWindow.shaperColorSpacesComboBox.setDisabled(True)
    mainWindow.outputColorSpacesComboBox.setDisabled(True)
    mainWindow.outputColorSpacesRadioButton.setDisabled(True)
    mainWindow.looksRadioButton.setDisabled(True)
    mainWindow.looksComboBox.setDisabled(True)
    mainWindow.iccDisplaysComboBox.setDisabled(True)
    mainWindow.iccDisplaysCheckBox.setDisabled(True)
    mainWindow.cubeSizeComboBox.setDisabled(True)
    mainWindow.shaperSizeComboBox.setDisabled(True)
    mainWindow.lutFormatComboBox.clear()

    mainWindow.lutFormatComboBox.addItems(LUT_FORMATS)
    mainWindow.cubeSizeComboBox.addItems(SIZES_LIST)
    mainWindow.shaperSizeComboBox.addItems(SIZES_LIST)

    mainWindow.cubeSizeComboBox.setCurrentIndex(32)
    mainWindow.shaperSizeComboBox.setCurrentIndex(32)

    mainWindow.inputColorSpacesComboBox.clear()
    mainWindow.shaperColorSpacesComboBox.clear()
    mainWindow.outputColorSpacesComboBox.clear()
    mainWindow.looksComboBox.clear()
    mainWindow.iccDisplaysComboBox.clear()

    mainWindow.processBakeLutPushButton.setDisabled(True)


def initializeUIWithConfigData(mainWindow, configData):
    """
    """
    ocioColorSpaces = configData["ocioColorSpaces"]
    ocioLooks = configData["ocioLooks"]
    ocioDisplays = configData["ocioDisplays"]

    mainWindow.inputColorSpacesComboBox.addItems(ocioColorSpaces)
    mainWindow.shaperColorSpacesComboBox.addItems(ocioColorSpaces)
    mainWindow.outputColorSpacesComboBox.addItems(ocioColorSpaces)
    mainWindow.looksComboBox.addItems(ocioLooks)
    mainWindow.iccDisplaysComboBox.addItems(ocioDisplays)

    mainWindow.inputColorSpacesComboBox.setEnabled(True)
    mainWindow.shaperColorSpacesCheckBox.setEnabled(True)
    mainWindow.shaperColorSpacesComboBox.setDisabled(True)
    mainWindow.outputColorSpacesRadioButton.setEnabled(True)
    mainWindow.outputColorSpacesComboBox.setEnabled(True)
    mainWindow.looksComboBox.setEnabled(True)
    mainWindow.iccDisplaysCheckBox.setEnabled(True)
    mainWindow.iccDisplaysComboBox.setEnabled(True)
    mainWindow.looksRadioButton.setEnabled(True)
    mainWindow.looksComboBox.setEnabled(True)

    mainWindow.outputColorSpacesRadioButton.setChecked(True)
    checkToEnableBaking(mainWindow)


def generateLutFileName(mainWindow, inputSpace, shaperSpace, outputSpace, looks, cubeSize, shaperSize, lutExt):
    """Generate the lut file name

    :param mainWindow: ocioLutPrescription mainWindow
    :param str inputSpace: the input colorspace
    :param str shaperSpace: the shaper colorspace
    :param str outputSpace: the output colorspace
    :param str looks: the look used
    :param str cubeSize: the cube size
    :param str shaperSize: the shaper size
    :param str lutExt: the lut extension

    :return: The lut file name
    :rtype: str
    """
    outDir = mainWindow.outputDirLineEdit.text()

    inputSpace = inputSpace.replace(" ", "_")
    if mainWindow.shaperColorSpacesCheckBox.checkState():
        shaperSpace = shaperSpace.replace(" ", "_")
        inputSpace = "_shaper_".join([inputSpace, shaperSpace])

    if outputSpace:
        output = outputSpace.replace(" ", "_")
    else:
        output = looks.replace(" ", "_")
    if mainWindow.cubeSizeCheckBox.checkState():
        output = "_c".join([output, cubeSize])
    if mainWindow.shaperSizeCheckBox.checkState():
        output = "_s".join([output, shaperSize])

    lutRadical = "_to_".join([inputSpace, output])

    lutFileName = os.path.join(outDir, ".".join([lutRadical, lutExt]))

    return lutFileName


def getBakeCmdData(mainWindow):
    """From the mainWindow, get all the data needed to build an ociobakelut command

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

    lutFileName = generateLutFileName(
        mainWindow, inputSpace, shaperSpace, outputSpace, looks, cubeSize, shaperSize, lutExt
    )

    bakeCmdData["lutFileName"] = lutFileName

    return bakeCmdData


def getOcioBakeLutCmd(bakeCmdData):
    """From the bake data dict, build a valid ociobakelut command

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


def ocioReport(bakeCmdData):
    """Basic report of the ociobakelut command

    :param dict bakeCmdData: data used to make the command
    """
    print("--------- LUT prescription -----------")
    print()
    print("OCIO: %s" % bakeCmdData["iconfig"][1])
    print("SEQ: %s" % os.environ.get("SEQ", "N/A"))
    print("SHOT: %s" % os.environ.get("SHOT", "N/A"))
    print("Input ColorSpace: %s" % bakeCmdData["inputSpace"][1])
    print("Shaper ColorSpace: %s" % bakeCmdData.get("shaperSpace", ["", "N/A"])[1])
    print("Output ColorSpace: %s" % bakeCmdData.get("outputSpace", ["", "N/A"])[1])
    print("Look: %s" % bakeCmdData.get("looks", ["", "N/A"])[1])
    print()
    print("LUT location: %s" % bakeCmdData["lutFileName"])
    print("--------------------------------------")


def saveSettings(settings, mainWindow):
    """
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


def loadSettings(settings, mainWindow):
    """
    """
    ocioConfigPath = settings.value("ocio/configPath")
    if not ocioConfigPath:
        initializeUIDefault(mainWindow)
    else:
        mainWindow.ocioCfgLineEdit.setText(ocioConfigPath)
        ocioConfigData = extractOCIOConfigData(ocioConfigPath)

        if ocioConfigData:
            initializeUIWithConfigData(mainWindow, ocioConfigData)

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

            mainWindow.lutFormatComboBox.addItems(LUT_FORMATS)

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
            mainWindow.processBakeLutPushButton.setEnabled(True)


def main():
    """main function
    """
    # Adds Ctrl+C support to kill app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.setOrganizationName("djieffx")
    app.setApplicationName("ocioLutPrescription")

    loader = QUiLoader()
    mainWindow = loader.load(os.path.join(os.path.dirname(__file__), "ocioLutPrescription_mainWindow.ui"))
    mainWindow.setWindowIcon(QIcon(":/icons/ocioLutPrescription_icon.png"))

    # initializeUIDefault(mainWindow)
    settings = QSettings()
    loadSettings(settings, mainWindow)

    @contextmanager
    def ocioContext():
        """
        :return:
        """
        seqContext = mainWindow.ocioSeqLineEdit.text()
        shotContext = mainWindow.ocioShotLineEdit.text()
        srcSeqEnvVar = os.environ.get("SEQ", None)
        srcShotEnvVar = os.environ.get("SHOT", None)

        if seqContext:
            os.environ["SEQ"] = seqContext

        if shotContext:
            os.environ["SHOT"] = shotContext

        yield

        if seqContext:
            if srcSeqEnvVar is None:
                del os.environ["SEQ"]
            else:
                os.environ["SEQ"] = srcSeqEnvVar

        if shotContext:
            if srcShotEnvVar is None:
                del os.environ["SHOT"]
            else:
                os.environ["SHOT"] = srcShotEnvVar

    def withOCIOContext():
        """
        :return:
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
        """from the UI, generate a valid ociobakelut command, and execute it"""
        bakeCmdData = getBakeCmdData(mainWindow)
        ocioBakeLutCmd = getOcioBakeLutCmd(bakeCmdData)
        subprocess.check_call(ocioBakeLutCmd)
        saveSettings(settings, mainWindow)
        ocioReport(bakeCmdData)

    mainWindow.ocioCfgLoadPushButton.clicked.connect(lambda x: browseForOcioConfig(mainWindow))
    mainWindow.outputDirBrowsePushButton.clicked.connect(lambda x: browseForLutOutputDir(mainWindow))
    mainWindow.ocioCfgLineEdit.textChanged.connect(lambda x: loadOCIOConfig(mainWindow))
    mainWindow.outputDirLineEdit.textChanged.connect(lambda x: checkToEnableBaking(mainWindow))
    mainWindow.processBakeLutPushButton.clicked.connect(processBakeLut)
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
