import zmq, pprint
import logging

logging.basicConfig(filename="applogs", format='%(asctime)s%(message)s', filemode='w')

__logger = logging.getLogger()
__logger.setLevel(logging.DEBUG)

class ZmqPublisher:
    
    def __init__(self):
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.PUB)
        self.__socket.bind("tcp://127.0.0.1:5555")

    def publish(self, message: dict):
        logging.debug('Sending message')
        self.__socket.send_json(message)
