"""
In this module, the bot logic is implemented.
"""
import telepot
from DomainMapper import tell_domain, predef_domains
from Brain import tell_relation

# Define a list of names that are used to refer to the interaction state.
S_READY = 0
S_DOMAIN = 1
S_DIRECTION = 2

class Chatbot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(Chatbot, self).__init__(*args, **kwargs)
        
        self._int_state = S_READY
        self.current_domain = None

    def on_chat_message(self, msg):

        # perform input validation
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type != 'text':
            self.sender.sendMessage("Please, only text messages for now :)")
            return

        # handle the message considering the interaction progess
        if self._int_state == S_READY:
            self.sender.sendMessage('Hey! What do you want to talk about?')
            self._int_state = S_DOMAIN
        
        elif self._int_state == S_DOMAIN:
            # msg should contain the domain we want to talk about
            # let's try to map it to one of the predefined ones.
            
            #TODO: intelligent domain lookup

            dom = tell_domain(msg['text'])
            if dom is None:
                self.sender.sendMessage("I didn't understand the domain. Please make sure it is correct.")
                return
            
            self.sender.sendMessage("You choose {} as domain. You start or should I?".format(predef_domains[dom]))
            self.current_domain = dom
            self._int_state = S_DIRECTION
            return

        elif self._int_state == S_DIRECTION:
            #TODO: intelligent direction inference
            if msg['text'].lower() == 'you':

                #TODO: enriching, the bot must ask a question about something
            
            else:

                relation = tell_relation(msg['text'])
                entities = tell_entities(msg['text'])

                #TODO: querying, look up for an answer
        
        else:
            self.sender.sendMessage('To be implemented.')
        pass