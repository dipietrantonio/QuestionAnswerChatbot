"""
In this module, the bot's logic of interaction is implemented.

The bot's behavior is described as a FSA having 5 states.
"""
import telepot
from Brain import answer_question, ask_question, analize_answer
from SentenceAnalysis import tell_domain, predefinedDomains
from Utilities import correct_grammatical_errors
import DataAccessManager
import time
from random import random
# Define a list of names that are used to refer to the interaction state.
S_START = 0                # beginning of the conversation
S_DOMAIN = 1               # choose a domain
S_DIRECTION = 2            # determine the direction of the conversation
S_WAITING_FOR_ANSWER = 3   # waiting for an answer from the user
S_ANOTHER_INPUT = 4

class Chatbot(telepot.helper.ChatHandler):
    """
    Represents a chat session with a Telegram user. Each time a user contacts the
    bot, telepot get the associated Chatbot instance from a pool. Each instance is
    associated to a single user, and runs on its own thread.
    """
    def __init__(self, *args, **kwargs):
        super(Chatbot, self).__init__(*args, **kwargs)
        # interaction state variable
        self._int_state = S_START
        self.current_domain = None
    
    def bot_ask_question(self):
        """
        ask a random question to a user and register the answer.
        """
        question, entity_1, relation = ask_question(self.current_domain)
        self.sender.sendMessage(question)
        self.enriching_data = (question, entity_1, relation)
        return

    def bot_answer_question(self, question):
        """
        answer a question and reply to the user.
        """
        ans = answer_question(correct_grammatical_errors(question))
        if ans is None:
            ans = "I don't know (or the question is not well formulated)."
        self.sender.sendMessage(ans)
    
    def record_answer(self, answer):

        question, entity_1, relation = self.enriching_data
        extracted_info = analize_answer(answer, entity_1)

        if extracted_info is None:
            self.sender.sendMessage("Are you sure the answer is correct? "\
            "I don't see any entity. Try to answer again!")
            return
        else:
            self.sender.sendMessage("I am recording the answer, wait..")
            entity_2 = extracted_info[1] + "::" + extracted_info[0]
            
            dataEntry = {
                'question' : question, 
                'answer'   : answer, 
                'relation' : relation, 
                'context' : "", 
                'domains' : [self.current_domain], 
                'c1' : entity_1, 
                'c2': entity_2
            }
            print("Sending data to server..")
            DataAccessManager.add_entry_to_knowledge_base(dataEntry)
            DataAccessManager.update_knowledge_graph()
            print("Local knowledge base updated.")
            self.next_interaction()

    def next_interaction(self):
        """
        decide randomly the next step of the discussion (ask or answer a question)
        """
        time.sleep(0.5)
        self.sender.sendMessage("Should I ask or you have a question? Reply 'ask me' to make"\
        " me ask a question, or send me a question directly.")
        self._int_state = S_DIRECTION

    def on_chat_message(self, msg):
        """
        This method is called on an incoming message from the user. The first thing
        to do is to determine the status of the conversation, i.e. the FSA state the
        chatbot is in.
        """
        # perform input validation
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type != 'text':
            self.sender.sendMessage("Please, only text messages for now :)")
            return

        # now, check if the message is a command that override the usual workflow
        if msg['text'] == '/domain': # this command is used to change domain
            self._int_state = S_START

        # handle the message considering the interaction progess
        if self._int_state == S_START:
            
            message = "Hi! I am here to answer your questions. And to ask you some too.\n"\
            "In case you can't answer to a question of mine, just reply 'I don't know'.\n"\
            "If you want to change domain, type '/domain'\n"\
            "\nWhat do you want to talk about? Reply with a domain."
            self.sender.sendMessage(message)

            # change state
            self._int_state = S_DOMAIN
        
        elif self._int_state == S_DOMAIN:
            # msg should contain the domain we want to talk about
            # let's try to map it to one of the predefined ones.
            
            domain = tell_domain(msg['text'])

            if domain is None:
                self.sender.sendMessage("I didn't understand the domain. Please make sure it is correct.")
                return
            
            self.sender.sendMessage("You chose {} as domain. You start or should I?".format(domain))
            self.sender.sendMessage("Reply 'ask me' to make me ask a question, or send me a question directly.")
            self.current_domain = domain
            self._int_state = S_DIRECTION
            return

        elif self._int_state == S_DIRECTION:
            if msg['text'].lower() in ['you', 'ask me', 'ask me anything']:
                self.bot_ask_question()
                self._int_state = S_WAITING_FOR_ANSWER

            else:
                self.bot_answer_question(msg['text'])
                self.next_interaction()
        
        elif self._int_state == S_WAITING_FOR_ANSWER:
            # record the answer
            answer = msg['text']

            if "i don't know" in answer.lower():
                self.next_interaction()
                return

            self.record_answer(answer)