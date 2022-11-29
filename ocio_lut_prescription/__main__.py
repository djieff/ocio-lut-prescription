# pylint: disable=no-name-in-module
"""UI Wrapper script over the "ociobakelut" command

Icon Copyright:
Prescription by Dam from the Noun Project
"""
from contextlib import contextmanager
from dataclasses import replace
from functools import partial, wraps
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


def main():
    """main application function"""
    # Adds Ctrl+C support to kill app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    env_ocio = os.environ.get("OCIO")
    env_sequence = os.environ.get("SEQ")
    env_shot = os.environ.get("SHOT")

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.setOrganizationName("djieffx")
    app.setApplicationName("ocio-lut-prescription")

    loader = QUiLoader()
    main_window = loader.load(
        os.path.join(os.path.dirname(__file__), "ui", "main_window.ui")
    )
    main_window.setWindowTitle("ocio-lut-prescription")
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
        bake_cmd_data = ui.BakeCmdData(*ui.get_bake_cmd_data(main_window))
        lut_name_param = {"lut_filename": core.get_lut_filename(bake_cmd_data)}
        bake_cmd_data = replace(bake_cmd_data, **lut_name_param)
        ociobakelut_cmd = core.get_ociobakelut_cmd(bake_cmd_data)

        with subprocess.Popen(
            ociobakelut_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            _, stderr = process.communicate()

            if process.returncode:
                main_window.resultLineEdit.setText("Error")
                main_window.resultLogTextEdit.setText(stderr.decode("utf-8"))
            else:
                main_window.resultLineEdit.setText(bake_cmd_data.lut_filename)
                stringed_log = core.ocio_report(bake_cmd_data, ociobakelut_cmd)
                main_window.resultLogTextEdit.setText(stringed_log)

    main_window.ocioCfgLoadPushButton.clicked.connect(
        partial(ui.browse_for_ocio_config, main_window, settings)
    )
    main_window.outputDirBrowsePushButton.clicked.connect(
        partial(ui.browse_for_lut_output_dir, main_window, settings)
    )
    main_window.ocioCfgLineEdit.textChanged.connect(
        partial(ui.load_ocio_config, main_window, settings)
    )
    main_window.outputDirLineEdit.textChanged.connect(
        partial(ui.check_to_enable_baking, main_window)
    )
    main_window.outputDirLineEdit.textChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.inputColorSpacesComboBox.currentIndexChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.outputColorSpacesComboBox.currentIndexChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.shaperColorSpacesComboBox.currentIndexChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.looksComboBox.currentIndexChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.lutFormatComboBox.currentIndexChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.lutFormatComboBox.currentIndexChanged.connect(
        partial(
            ui.check_for_icc, main_window, main_window.lutFormatComboBox.currentText()
        )
    )
    main_window.cubeSizeComboBox.currentIndexChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.shaperSizeComboBox.currentIndexChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.iccWhitePointLineEdit.textChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.iccDisplaysComboBox.currentIndexChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.iccDescriptionLineEdit.textChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.iccCopyrightLineEdit.textChanged.connect(
        partial(ui.save_settings, settings, main_window)
    )
    main_window.actionSetDarkStyle.triggered.connect(
        partial(ui.set_dark_style, app, settings)
    )
    main_window.actionSetSystemStyle.triggered.connect(
        partial(ui.set_system_style, app, settings)
    )
    main_window.actionSettingsClear.triggered.connect(
        partial(ui.settings_clear, app, settings, main_window)
    )
    main_window.processBakeLutPushButton.clicked.connect(process_bake_lut)

    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
