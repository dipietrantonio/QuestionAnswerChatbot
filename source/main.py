"""
A Telegram Chatbot that is able to answer questions about stuff.

Author: Cristian Di Pietrantonio, 2017

This is the main module that starts the system. It is a multiprocess
application. Two processes are started, one running the
QuestionClassifier server (assign to each question a relation)
and the other handles messages from users. They interact using a simple
protocol over TCP.
"""
import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from multiprocessing.context import Process

import DataAccessManager
from Chatbot import Chatbot
from QuestionClassifier import get_question_classifier
from RemoteClassifier import RemoteClassifierServer
from Settings import QuestionClassifierServer_Host, QuestionClassifierServer_Port, TelegramBotToken


def start_question_classifier_server(host, port):
    """
    start the process that hosts the question classifier server.
    """
    qc = get_question_classifier()
    rc = RemoteClassifierServer(qc, host, port)
    rc.activate()

if __name__ == "__main__":

    # Start question classifier process
    p = Process(target=start_question_classifier_server, args=(QuestionClassifierServer_Host, QuestionClassifierServer_Port,))
    p.start()
    
    # load database
    DataAccessManager.initialize_knowledge_graph()
    bot = telepot.DelegatorBot(TelegramBotToken, [ pave_event_space()(per_chat_id(), create_open, Chatbot, timeout=1000), ])
    MessageLoop(bot).run_as_thread()
    print('Listening..')

    try:
        while 1:
            time.sleep(10)
    except KeyboardInterrupt:
        sys.exit()