# QuestionAnswer Chatbot

This project implements a simple telegram chatbot that is able to answer to and to formulate questions
about concepts belonging to predefined domains, and that are linked together through a predefined set
of relations.

The chatbot is backed with a dataset of question - answer pairs about a set of concepts. From this set,
we can both pick answers for new questions, or pick subjects and topics for new questions to ask users.

# Dependencies
First of all, this program targets Python 3.5.x or higher. The following external libraries are required 
to run the code:

    *   `SpaCy`
    *   `nltk`
    *   `keras`

In addition, the local files are needed to run the system without a preprocess of configuration and download of
the dataset, so don't delete it.

Important: the system uses communication over TCP between two processes on the same machine (but they could be on 
different machines in a hypothetical production environment), so make sure you don't have particular firewall
rules that block traffic on localhost.

# How To Run
To run the system, open a terminal in the `source` folder and simply type ``python main.py``. 
It will start the necessary processes and will print debug information. When it prints `listening..` the system is ready to receive messages.

You can contact the bot through telegram, the useranme is `@dipietra_bot`
