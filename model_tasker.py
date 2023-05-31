import sys
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QInputDialog, QMessageBox, QVBoxLayout, QPushButton
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QWaitCondition, QMutex

from dotenv import load_dotenv
load_dotenv()

from tasker import Tasker # type: ignore
from models import DefinitionModel, TypewriteModel, EchoModel, PythonREPLModel, CommandModel

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ModelRunner(QObject):
    finished = pyqtSignal(str)
    show_dialog = pyqtSignal()
    def __init__(self, model, word):
        super(ModelRunner, self).__init__()
        self.wait_condition = QWaitCondition()
        self.mutex = QMutex()
        logger.debug('Initializing ModelRunner')
        self.model = model
        self.word = word
    def run(self):
        logger.debug('ModelRunner running')
        self.model.run(self.word, wait=self.wait_condition, mutex=self.mutex, show_dialog=self.show_dialog)
        logger.debug('ModelRunner done')
        self.finished.emit("Replace with LLM result")
    def input_received(self, cont):
        self.model.custom_handler.cont = cont
        self.wait_condition.wakeOne()

class SimpleInputDialog(QWidget):
    def __init__(self, model_runner):
        super().__init__()
        self.model_runner = model_runner
    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')

        if ok:
            QMessageBox.information(self, "Entered Text", "You entered: " + text)
            if text == 'y':
                self.model_runner.input_received(True)
            else:
                self.model_runner.input_received(False)

class CustomTasker(Tasker):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.custom_menu()
        
        # self.window.show()
        self.setQuitOnLastWindowClosed(False)
        
        self.model_runner_thread = QThread()
        
    def custom_menu(self):
        self.submenu = QMenu('Models')
        # TODO: Does thise save state?
        self.model_mapping = {
            'Echo Model': EchoModel(self.screen),
            'Typewrite Model': TypewriteModel(),
            'Definition Model': DefinitionModel(self.screen),
            'Python REPL Model': PythonREPLModel(self),
            'Command Model': CommandModel(self.screen),
        }
        # for key, model in self.model_mapping.items():
        #     print(f'Option: {key}, Class Name: {model.__class__.__name__}')

        
        self.options = [QAction(f"{i}", checkable=True) for i, _ in self.model_mapping.items()]
        for option in self.options:
            option.toggled.connect(self.submenu_handle_toggled)
            self.submenu.addAction(option)
        self.options[0].setChecked(True)
        
        self.tray_menu.insertMenu(self.tray_menu.actions()[0], self.submenu)
        
    def submenu_handle_toggled(self, checked):
        action = self.sender()
        if checked:
            logger.debug(f"Activating {action.text()}")
            self.model = self.model_mapping[action.text()]
            for option in self.options:
                if option != action:
                    option.setChecked(False)
        
    def model_runner_callback(self, transcription):
        logger.debug("From model runner thread: " + transcription)
        
    def transcriber_callback(self, transcription):
        # transcription_words = transcription.split(" ")
        # word = transcription_words[0]
        logger.debug('Transcription: ' + transcription)
        
        
        if self.model_runner_thread.isRunning():
            logger.debug('ModelRunner was running')
            self.model_runner_thread.quit()
            self.model_runner_thread.wait()
        self.model_runner_thread = QThread()
        self.model_runner = ModelRunner(self.model, transcription)
        self.model_runner.moveToThread(self.model_runner_thread)
        self.model_runner_thread.started.connect(self.model_runner.run)
        self.window = SimpleInputDialog(self.model_runner)
        self.model_runner.show_dialog.connect(self.window.showDialog)
        self.model_runner.finished.connect(self.model_runner_callback)
        self.model_runner_thread.start()

if __name__ == '__main__':
    app = CustomTasker(sys.argv)
    sys.exit(app.exec_())