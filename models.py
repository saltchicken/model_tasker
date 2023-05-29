from dotenv import load_dotenv
load_dotenv()

import os, sys, time, pyautogui
from langchain import OpenAI, LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents.agent_toolkits import create_python_agent
from langchain.tools.python.tool import PythonREPLTool
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional, Union
from langchain.schema import (
    AgentAction,
    AgentFinish,
    BaseMessage,
    LLMResult,
)
from langchain.python import PythonREPL

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

class DefinitionModel():
    def __init__(self, screen):
        self.screen = screen
        self.llm = OpenAI(temperature=.7)
        self.template = """You are a dictionary. Tell me the meaning of {word}.

        Word: {word}
        Definition: This is the definition:"""
        self.prompt_template = PromptTemplate(input_variables=['word'], template=self.template)
        self.definition_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    def run(self, word):
        self.screen.write(word)
        # TODO Make this a QThread   
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
    def run(self, word):
        pyautogui.typewrite(word)
        # pyautogui.press('enter')
        
class EchoModel():
    def __init__(self, screen):
        self.screen = screen
    def run(self, word):
        self.screen.write(word)
        
        
class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        print(self.app.worker)
    # def on_llm_new_token(self, token: str, **kwargs) -> None:
    #     print(f"My custom handler, token: {token}")
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        # user_input = input("Do you want to continue? (y/N): ")
        # if user_input.lower() == "y":
        #     print("Continuing the program...")
        # else:
        #     sys.exit(1)
        print("Tool starting...")
        cont = self.app.window.showDialog()
        if not cont:
            # TODO: Should not be closing the whole app. Stop only agentChain
            sys.exit(1)
        print("Tool continuing...")
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        print(action, kwargs)
            
class PythonREPLModel():
    def __init__(self, app):
        self.app = app
        self.agent_executor = create_python_agent(
        # llm=OpenAI(temperature=0, max_tokens=1000, streaming=True, callbacks=[MyCustomHandler()]),
        llm=OpenAI(temperature=0, max_tokens=1000),
        tool=PythonREPLTool(),
        verbose=True
    )
    def run(self, goal):
        # agent_executor.run(goal, callbacks=[MyCustomHandler()])
        self.agent_executor.run("""Understand, write a python script that will print "hello world""", callbacks=[MyCustomHandler(self.app)])
