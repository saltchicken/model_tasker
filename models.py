from dotenv import load_dotenv
load_dotenv()

import os, sys, time, string, pyautogui
from langchain import OpenAI, LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents.agent_toolkits import create_python_agent
from langchain.tools.python.tool import PythonREPLTool
from langchain.python import PythonREPL
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional, Union
from langchain.schema import (
    AgentAction,
    AgentFinish,
    BaseMessage,
    LLMResult,
)
from elevenlabslib import *

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def say_elvenlabs(text):
    user = ElevenLabsUser(os.getenv("ELEVENLABS_KEY"))
    voice = user.get_voices_by_name("Rachel")[0]
    voice.generate_and_play_audio(text, playInBackground=False)

def remove_punctuation_except_apostrophe(input_string):
    all_except_apostrophe = string.punctuation.replace("'", "")
    translator = str.maketrans('', '', all_except_apostrophe)
    return input_string.translate(translator)

def focus(window):
    logger.debug("TODO: [Focus] " + window)
    
def switch_desktop(direction):
    if direction == 'right':
        pyautogui.hotkey('win', 'ctrl', 'right')
    elif direction == 'left':
        pyautogui.hotkey('win', 'ctrl', 'left')
    else:
        logger.debug("direction not found")
    
class CommandModel():
    def __init__(self, screen):
        self.screen = screen
        self.command_mapping = {
            'focus': focus,
            'switch': switch_desktop,
        }
        
    def run(self, transcription, **kwargs):
        command = remove_punctuation_except_apostrophe(transcription)
        command = command.lower().split(" ")
        logger.debug(f"CommandModel received command: {command}")
        # TODO Implement single word commands and clean up this len check. Need for more robust command handling.
        if len(command) >= 2:
            key = command[0]
            param1 = command[1]
            if key in self.command_mapping:
                logger.debug(f"CommandModel Running key: {key} param1: {param1}")
                execute = self.command_mapping[key]
                execute(param1)
            else:
                logger.debug("command not found")
        else:
            logger.debug("command not found")
        
class DefinitionModel():
    def __init__(self, screen):
        self.screen = screen
        self.llm = OpenAI(temperature=.7)
        self.template = """You are a dictionary. Tell me the meaning of {word}.

        Word: {word}
        Definition: This is the definition:"""
        self.prompt_template = PromptTemplate(input_variables=['word'], template=self.template)
        self.definition_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    def run(self, word, **kwargs):
        self.screen.write(word)
        # result = self.definition_chain({"word": word})
        # say_elvenlabs(result['text'])
        
        # For testing without API
        logger.debug('running LLM...')
        result = "BOGUS"
        time.sleep(2)
        logger.debug('Done with LLM')
        logger.debug('Speaking output...')
        time.sleep(3)
        logger.debug('Done speaking output')

class TypewriteModel():
    def __init__(self):
        pass
    def run(self, word, **kwargs):
        pyautogui.typewrite(word)
        # pyautogui.press('enter')
        
class EchoModel():
    def __init__(self, screen):
        self.screen = screen
    def run(self, word, **kwargs):
        self.screen.write(word)
        
class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, wait, mutex, show_dialog) -> None:
        super().__init__()
        self.wait = wait
        self.mutex = mutex
        self.show_dialog = show_dialog
        self.cont = None
    # def on_llm_new_token(self, token: str, **kwargs) -> None:
    #     print(f"My custom handler, token: {token}")
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        logger.debug("Tool starting...")
        self.show_dialog.emit()
        self.mutex.lock()
        self.wait.wait(self.mutex)
        self.mutex.unlock()
        if self.cont == None:
            logger.debug("CRITICAL ERROR: No cont provided")
        if self.cont == False:
            # TODO: This kills the ModelRunner thread and breaks the app. Doesn't finish execution which is critical to continue main thread.
            sys.exit(1)
        logger.debug("Tool continuing...")
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        # logger.debug(action)
        # TODO Determine what kwargs can be used for
        print(action, kwargs)
            
class PythonREPLModel():
    def __init__(self, app):
        self.app = app
        self.agent_executor = create_python_agent(
        # llm=OpenAI(temperature=0, max_tokens=1000, streaming=True, callbacks=[MyCustomHandler()]),
        llm=OpenAI(temperature=0, max_tokens=1000),
        tool=PythonREPLTool(),
        verbose=True,
        # return_intermediate_steps = True
    )
        
    def run(self, goal, **kwargs):
        # agent_executor.run(goal, callbacks=[MyCustomHandler()])
        
        self.custom_handler = MyCustomHandler(kwargs['wait'], kwargs['mutex'], kwargs['show_dialog'])
        if 'wait' in kwargs and 'mutex' in kwargs and 'show_dialog' in kwargs:
            self.agent_executor.run("""Understand, write a python script that will print "hello world""", callbacks=[self.custom_handler])
        else:
            logger.debug("No wait or mutex or show_dialog or cont provided")