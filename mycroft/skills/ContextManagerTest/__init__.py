# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from adapt.context import ContextManager
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from time import sleep

__author__ = 'jarbas'

logger = getLogger(__name__)

client = None

class ContextSkill(MycroftSkill):

    def __init__(self):
        super(ContextSkill, self).__init__(name="ContextSkill")
        self.context_dict = {} #override examples for using in this skill
        self.intents_dict = {}
        self.signals_dict = {}
        self.skills_dict = {}
        self.results_dict = {}

    def initialize(self):
        #self.load_data_files(dirname(__file__))

        context_intent = IntentBuilder("ContextTestIntent")\
            .require("contextKeyword").build()
        self.register_intent(context_intent,
                             self.handle_context_intent)

        general_context_intent = IntentBuilder("GeneralContextIntent") \
            .require("GcontextKeyword").build()
        self.register_intent(general_context_intent,
                             self.handle_general_context_intent)

        signal_context_intent = IntentBuilder("SignalContextIntent") \
            .require("SigcontextKeyword").build()
        self.register_intent(signal_context_intent,
                             self.handle_signals_context_intent)

        intents_context_intent = IntentBuilder("IntentsContextIntent") \
            .require("IcontextKeyword").build()
        self.register_intent(intents_context_intent,
                             self.handle_intents_context_intent)

        skills_context_intent = IntentBuilder("SkillsContextIntent") \
            .require("ScontextKeyword").build()
        self.register_intent(skills_context_intent,
                             self.handle_skills_context_intent)

        results_context_intent = IntentBuilder("ResultsContextIntent") \
            .require("RcontextKeyword").build()
        self.register_intent(results_context_intent,
                             self.handle_results_context_intent)

        self.emitter.on("context_result", self.handle_context_result)   ### only thing you need to have context in your skill!
        #### receives the following data
        #  Message("context_result", {'full_dictionary': self.context_dict,'bluetooth': self.bluetooth_dict, 'abstract': self.abstract_dict, 'signals': self.signals_dict, 'results': self.results_dict, 'intents': self.intents_dict,'regex': self.regex_dict,'skills': self.skills_dict})

    def handle_context_intent(self, message):
        self.emitter.emit(Message("context_request")) #update context
        while not self.context_flag:
            pass #wait results response
        self.speak_dialog("ctxt")

        contexts = self.manager.get_context()

        #adapt way
        for ctxt in contexts:
            if ctxt["data"] is not None:
                self.speak(ctxt["key"] + " has value " + ctxt["data"])

        self.context_flag = False

    def handle_general_context_intent(self, message):
        self.emitter.emit(Message("context_request")) #update context
        while not self.context_flag:
            pass #wait results response
        self.speak_dialog("override")

        for key in self.context_dict:
            if self.context_dict[key] is not None:
                text = key + " context has value " + str(self.context_dict[key])
                self.speak(text)

        self.context_flag = False

    def handle_signals_context_intent(self, message):
        self.emitter.emit(Message("context_request")) #update context
        while not self.context_flag:
            pass #wait results response
        self.speak_dialog("override")

        for key in self.signals_dict:
            if self.signals_dict[key] is not None:
                text = key + " signal context has value " + str(self.signals_dict[key])
                self.speak(text)

        self.context_flag = False

    def handle_intents_context_intent(self, message):
        self.emitter.emit(Message("context_request"))  # update context
        while not self.context_flag:
            pass  # wait results response
        self.speak_dialog("override")

        for key in self.intents_dict:
            if self.intents_dict[key] is not None:
                text = key + " intent context has value " + str(self.intents_dict[key])
                self.speak(text)

        self.context_flag = False

    def handle_skills_context_intent(self, message):
        self.emitter.emit(Message("context_request"))  # update context
        while not self.context_flag:
            pass  # wait results response
        self.speak("the following skills are available")

        for key in self.skills_dict: ### dont have any good values, just skill name for now
            text = key + " skill"
            self.speak(text)

        self.context_flag = False

    def handle_results_context_intent(self, message):
        self.emitter.emit(Message("context_request"))  # update context
        while not self.context_flag:
            pass  # wait results response
        self.speak_dialog("override")

        for key in self.results_dict:
            if self.results_dict[key] is not None:
                text = key + " result context has value " + str(self.results_dict[key])
                self.speak(text)

        self.context_flag = False

    ###### only if you need to override, function already in core
    def handle_context_result(self, message):
        #### this is the default function getting all regex contexts

        dict = message.data["regex"] #should i get all context or just regex? theres lot of "useless" stuff in there
        for key in dict:
            # adapt way
            if dict[key] is not None:
                entity = {'key': key, 'data': dict[key], 'confidence': 1.0}
                # check for duplicates before injecting,  shouldnt this be auto-handled by adapt?
                contexts = self.manager.get_context()
                flag = False
                for ctxt in contexts:
                    if ctxt["key"] == key and ctxt["data"] == dict[key]:
                        flag = True  # its duplicate!
                if not flag:
                    self.manager.inject_context(entity)
                    print "injecting " + str(entity)

        #### override example for more context data, not using adapt on purpose just to show different aproach

        dict = message.data["abstract"]
        for key in dict:
                # build skill dict for testing
                self.context_dict.setdefault(key, dict[key])

        dict = message.data["signals"]
        for key in dict:
            # build skill dict for testing
            self.signals_dict.setdefault(key, dict[key])

        dict = message.data["intents"]  # should i get all context or just regex?
        for key in dict:
            # build skill dict for testing
            self.intents_dict.setdefault(key, dict[key])

        dict = message.data["results"]  # should i get all context or just regex?
        for key in dict:
            # build skill dict for testing
            self.results_dict.setdefault(key, dict[key])

        dict = message.data["skills"]  # should i get all context or just regex?
        for key in dict:
            # build skill dict for testing
            self.skills_dict.setdefault(key)

        self.context_flag = True

    def override_ctxt(self, key, result):
        self.emitter.emit(Message("context_key_override", {"key":key,"value":result}))  # update context with new value


    def stop(self):
        pass


def create_skill():
    return ContextSkill()
