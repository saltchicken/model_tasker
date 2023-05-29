from dotenv import load_dotenv
load_dotenv()

import os, pyautogui
from langchain import OpenAI, LLMChain
from langchain.prompts import PromptTemplate

from elevenlabslib import *

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
        result = self.definition_chain({"word": word})
        say_elvenlabs(result['text'])

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
