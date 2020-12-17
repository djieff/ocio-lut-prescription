"""UI Wrapper script over the "ociobakelut" command

Icon Copyright:
Prescription by Dam from the Noun Project
"""
from contextlib import contextmanager
from functools import wraps
import os
import signal
import subprocess
import sys

from ocioLutPrescription.olp_modules import core, ui

from PySide2.QtCore import Qt, QCoreApplication, QSettings
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon, QIntValidator

from ocioLutPrescription.ui_files import ocioLutPrescription_qrc


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
    mainWindow = loader.load(
        os.path.join(os.path.dirname(__file__), "ui_files", "ocioLutPrescription_mainWindow.ui")
    )
    mainWindow.setWindowIcon(QIcon(":/icons/ocioLutPrescription_icon.png"))
    mainWindow.iccWhitePointLineEdit.setValidator(QIntValidator(1, 10000))

    settings = QSettings()
    if env_ocio:
        mainWindow.ocioCfgLineEdit.setText(env_ocio)
        mainWindow.ocioSeqLineEdit.setText(env_sequence)
        mainWindow.ocioShotLineEdit.setText(env_shot)
        ui.load_ocio_config(mainWindow, settings)
    else:
        ui.load_settings(app, settings, mainWindow)

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
        bake_cmd_data = ui.get_bake_cmd_data(mainWindow)
        lut_result_file = bake_cmd_data["lut_filename"]
        ociobakelut_cmd = core.get_ociobakelut_cmd(bake_cmd_data)

        process = subprocess.Popen(ociobakelut_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode:
            mainWindow.resultLineEdit.setText("Error")
            mainWindow.resultLogTextEdit.setText(stderr.decode("utf-8"))
            print(" ".join(ociobakelut_cmd))
        else:
            mainWindow.resultLineEdit.setText(lut_result_file)
            stringedLog = core.ocio_report(bake_cmd_data, ociobakelut_cmd)
            mainWindow.resultLogTextEdit.setText(stringedLog)

    mainWindow.ocioCfgLoadPushButton.clicked.connect(
        lambda x: ui.browse_for_ocio_config(mainWindow, settings)
    )
    mainWindow.outputDirBrowsePushButton.clicked.connect(
        lambda x: ui.browse_for_lut_output_dir(mainWindow, settings)
    )
    mainWindow.ocioCfgLineEdit.textChanged.connect(
        lambda x: ui.load_ocio_config(mainWindow, settings)
    )
    mainWindow.outputDirLineEdit.textChanged.connect(
        lambda x: ui.check_to_enable_baking(mainWindow)
    )
    mainWindow.outputDirLineEdit.textChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.inputColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.outputColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.shaperColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.looksComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.lutFormatComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.lutFormatComboBox.currentIndexChanged.connect(
        lambda x: ui.check_for_icc(mainWindow, mainWindow.lutFormatComboBox.currentText())
    )
    mainWindow.cubeSizeComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.shaperSizeComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.iccWhitePointLineEdit.textChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.iccDisplaysComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.iccDescriptionLineEdit.textChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.iccCopyrightLineEdit.textChanged.connect(
        lambda x: ui.save_settings(settings, mainWindow)
    )
    mainWindow.actionSetDarkStyle.triggered.connect(
        lambda x: ui.set_dark_style(app, settings)
    )
    mainWindow.actionSetSystemStyle.triggered.connect(
        lambda x: ui.set_system_style(app, settings)
    )
    mainWindow.actionSettingsClear.triggered.connect(
        lambda x: ui.settings_clear(app, settings, mainWindow)
    )
    mainWindow.processBakeLutPushButton.clicked.connect(process_bake_lut)

    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
