# pylint: disable=no-name-in-module
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

from PySide2.QtCore import (
    Qt,
    QCoreApplication,
    QSettings,
)
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon, QIntValidator

from ocio_lut_prescription import core
from ocio_lut_prescription.core import ui
from ocio_lut_prescription.ui import qrc  # pylint: disable=unused-import


def main():  # pylint: disable=too-many-statements
    """main application function"""
    # Adds Ctrl+C support to kill app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    env_ocio = os.environ.get("OCIO")
    env_sequence = os.environ.get("SEQ")
    env_shot = os.environ.get("SHOT")

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.setOrganizationName("djieffx")
    app.setApplicationName("ocio_lut_prescription")

    loader = QUiLoader()
    main_window = loader.load(
        os.path.join(os.path.dirname(__file__), "ui", "main_window.ui")
    )
    main_window.setWindowIcon(QIcon(":/icons/icon.png"))
    main_window.iccWhitePointLineEdit.setValidator(QIntValidator(1, 10000))

    settings = QSettings()
    if env_ocio:
        main_window.ocioCfgLineEdit.setText(env_ocio)
        main_window.ocioSeqLineEdit.setText(env_sequence)
        main_window.ocioShotLineEdit.setText(env_shot)
        ui.load_ocio_config(main_window, settings)
    else:
        ui.load_settings(app, settings, main_window)

    @contextmanager
    def ocio_context():
        """Keep current ocio context in memory, in case values are overriden in the UI"""
        sequence_context = main_window.ocioSeqLineEdit.text()
        shot_context = main_window.ocioShotLineEdit.text()

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
        """decorator which allows running functions in an ocio context"""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with ocio_context():
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    @with_ocio_context()
    def process_bake_lut():
        """from the UI, generate a valid ociobakelut command, and execute it"""
        bake_cmd_data = ui.get_bake_cmd_data(main_window)
        lut_result_file = bake_cmd_data["lut_filename"]
        ociobakelut_cmd = core.get_ociobakelut_cmd(bake_cmd_data)

        process = subprocess.Popen(
            ociobakelut_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        _, stderr = process.communicate()

        if process.returncode:
            main_window.resultLineEdit.setText("Error")
            main_window.resultLogTextEdit.setText(stderr.decode("utf-8"))
            print(" ".join(ociobakelut_cmd))
        else:
            main_window.resultLineEdit.setText(lut_result_file)
            stringed_log = core.ocio_report(bake_cmd_data, ociobakelut_cmd)
            main_window.resultLogTextEdit.setText(stringed_log)

    main_window.ocioCfgLoadPushButton.clicked.connect(
        lambda x: ui.browse_for_ocio_config(main_window, settings)
    )
    main_window.outputDirBrowsePushButton.clicked.connect(
        lambda x: ui.browse_for_lut_output_dir(main_window, settings)
    )
    main_window.ocioCfgLineEdit.textChanged.connect(
        lambda x: ui.load_ocio_config(main_window, settings)
    )
    main_window.outputDirLineEdit.textChanged.connect(
        lambda x: ui.check_to_enable_baking(main_window)
    )
    main_window.outputDirLineEdit.textChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.inputColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.outputColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.shaperColorSpacesComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.looksComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.lutFormatComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.lutFormatComboBox.currentIndexChanged.connect(
        lambda x: ui.check_for_icc(
            main_window, main_window.lutFormatComboBox.currentText()
        )
    )
    main_window.cubeSizeComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.shaperSizeComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.iccWhitePointLineEdit.textChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.iccDisplaysComboBox.currentIndexChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.iccDescriptionLineEdit.textChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.iccCopyrightLineEdit.textChanged.connect(
        lambda x: ui.save_settings(settings, main_window)
    )
    main_window.actionSetDarkStyle.triggered.connect(
        lambda x: ui.set_dark_style(app, settings)
    )
    main_window.actionSetSystemStyle.triggered.connect(
        lambda x: ui.set_system_style(app, settings)
    )
    main_window.actionSettingsClear.triggered.connect(
        lambda x: ui.settings_clear(app, settings, main_window)
    )
    main_window.processBakeLutPushButton.clicked.connect(process_bake_lut)

    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()