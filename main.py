import sys
import time
from bs4 import BeautifulSoup
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from Chatbot import Chatbot

# read data from telegram settings file
settings = open('bot.xml').read()
soup = BeautifulSoup(settings, 'lxml')
token = soup.find('token').text

bot = telepot.DelegatorBot(token, [ pave_event_space()(per_chat_id(), create_open, Chatbot, timeout=100), ])
MessageLoop(bot).run_as_thread()
print('Listening..')

while 1:
    time.sleep(10)