import sys
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QInputDialog, QMessageBox, QVBoxLayout, QPushButton

from dotenv import load_dotenv
load_dotenv()

from tasker import Tasker # type: ignore
from models import DefinitionModel, TypewriteModel, EchoModel, PythonREPLModel

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

import string

def remove_punctuation_except_apostrophe(input_string):
    all_except_apostrophe = string.punctuation.replace("'", "")
    translator = str.maketrans('', '', all_except_apostrophe)
    return input_string.translate(translator)

class SimpleInputDialog(QWidget):
    def __init__(self):
        super().__init__()

    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')

        if ok:
            QMessageBox.information(self, "Entered Text", "You entered: " + text)
            if text == 'y':
                return True
            else:
                return False

class CustomTasker(Tasker):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.custom_menu()
        self.window = SimpleInputDialog()
        # self.window.show()
        self.setQuitOnLastWindowClosed(False)
        
    def custom_menu(self):
        self.submenu = QMenu('Models')
        # TODO: Does thise save state?
        self.model_mapping = {
            'Echo Model': EchoModel(self.screen),
            'Typewrite Model': TypewriteModel(),
            'Definition Model': DefinitionModel(self.screen),
            'Python REPL Model': PythonREPLModel(self),
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
            logger.debug(self.model)
            for option in self.options:
                if option != action:
                    option.setChecked(False)
        
    def transcriber_callback(self, transcription):
        # transcription_words = transcription.split(" ")
        # word = transcription_words[0]
        word = remove_punctuation_except_apostrophe(transcription)
        logger.debug(word)
        self.model.run(word)

if __name__ == '__main__':
    app = CustomTasker(sys.argv)
    sys.exit(app.exec_())