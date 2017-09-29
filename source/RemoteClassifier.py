"""
    This module implements the class `RemoteClassifierServer`. It is a containter for a
    Machine Learning classifier that enables the classifier to be used through an
    IP network.
"""
import socket
import socketserver
from threading import Thread, Lock
import time
import pickle


def remote_predict(data, host, port):
    """
    Request a predict call to a remote classifier.

    Parameters:
    -----------
        - data: data to use as argument to the predict function. 
        - host: host name where to send data to
        - port: port the server is listening to
    
    Returns:
    --------
        - predicted data. 
    """
    s = socket.socket()
    host = socket.gethostbyname(host)
    s.connect((host, port))
    _send_socket(data, s)
    message = _recv_socket(s)
    s.close()
    return message

def _send_socket(data, sock):
    """
    Send data through a socket.

    This method serializes the object and, together with _recv_socket, implements
    a simple protocol where the first 5 bytes sent are the length of the sequence 
    of bytes transmitted next.

    Parameters:
    -----------
        - data: data to be sent
        - sock: socket to use for transmission
    
    Returns:
    --------
    Nothing
    """
    data_dump = pickle.dumps(data)
    data_length = pickle.dumps(len(data_dump))
    sock.send(data_length)
    sock.send(data_dump)

def _recv_socket(sock):
    """
    Receive data through a socket.
    
    This method receives the object as sequence of bytes and, together with 
    _send_socket, implements a simple protocol where the first 5 bytes received 
    are the length of the incoming sequence of bytes.

    Parameters:
    -----------
        - sock: socket used for communication.

    Returns:
    --------
    An object 
    """
    length = pickle.loads(sock.recv(5))
    message = b""
    total_received = 0
    while len(message) < length:
        current = sock.recv(length - total_received)
        if current is None or len(current) == 0:
            break
        total_received += len(current)
        message += current
    message = pickle.loads(message)
    return message

def _process_request_async(c, addr, classifier):
    """
    handle an incoming connection from a client.

    Parameters:
    -----------
        - c: client socket
        - addr: client address
        - classifier: reference to the classifier object
    """
    # the first 5 bytes tells the length of the message
    message = _recv_socket(c)
    classifier._enqueue_predict_request(c, message)
    return

def _server_listener_fuction(classifier):
    """
    listen for incoming connections from clients.

    Parameters:
    -----------
        - classifier: reference to the RemoteClassifier object
    """
    while True:
        c, addr = classifier._sockServer.accept()
        Thread(target=_process_request_async, args=(c, addr, classifier)).start()

class RemoteClassifierServer:
    """
    A container for a classifier that implements the `predict` method. It enables
    the classifier to be contacted through the network.
    """
    def __init__(self, clf, host, port):
        self._queue = list()
        self._queueLock = Lock()
        self._clf = clf
        self._sockServer = socket.socket()
        host = socket.gethostbyname(host)
        self._sockServer.bind((host, port))

    def _enqueue_predict_request(self, client, data):
        """
        Add a predict request to the requests queue.

        Parameters:
        -----------
            - client: the client socket the request came from
            - data: data arrived from the socket
        
        Returns:
        --------
            Nothing
        """
        self._queueLock.acquire()
        try:
            self._queue.insert(0, (client, data))
        finally:
            self._queueLock.release()
        return

    def _pop_predict_request(self):
        """
        Takes a request form the requests queue for processing it.
        """

        self._queueLock.acquire()
        popped_item = None
        try:
            if len(self._queue) > 0:
                popped_item = self._queue.pop()
        finally:
            self._queueLock.release()
        return popped_item
    
    def activate(self):
        """
        Make the classifier start listening for prediction requests.
        """
        self._sockServer.listen(100)
        self._listener_thread = Thread(target=_server_listener_fuction, args=(self,))
        self._listener_thread.start()

        # go on checking for prediction requests
        while True:
            time.sleep(0.3)
            req = self._pop_predict_request()
            if req is None:
                continue

            client, data = req
            y_pred = self._clf.predict(data)
            _send_socket(y_pred, client)
            client.close()