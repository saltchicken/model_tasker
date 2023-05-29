import sys
from PyQt5.QtWidgets import QMenu, QAction

from dotenv import load_dotenv
load_dotenv()

from tasker import Tasker
from models import DefinitionModel, TypewriteModel, EchoModel

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class CustomTasker(Tasker):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.custom_menu()
        
    def custom_menu(self):
        self.submenu = QMenu('Models')
        # TODO: Does thise save state?
        self.model_mapping = {
            'Echo Model': EchoModel(self.screen),
            'Typewrite Model': TypewriteModel(),
            'Definition Model': DefinitionModel(self.screen),
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
        word = transcription
        logger.debug(word)
        self.model.run(word)
        # TODO: Fixed by sending signal through begin_recording()
        if self.worker.quit == False:
            self.worker.running = True

if __name__ == '__main__':
    app = CustomTasker(sys.argv)
    sys.exit(app.exec_())