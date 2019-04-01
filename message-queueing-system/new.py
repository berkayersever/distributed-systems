from multiprocessing import Process
import os
import math
import zmq
from abc import ABC, abstractmethod


class MapReduce(ABC):
    numWorkerProcess = []
    pProducer = None
    pResultCollector = None

    def __init__(self, NumWorker):
        self.NumWorker = NumWorker
        super().__init__()

    @abstractmethod
    def Map(self, data_arr):
        self.data_arr_map = data_arr

    @abstractmethod
    def Reduce(self, data_arr):
        self.data_arr_reduce = data_arr

    def __producer(self, data_arr):
        self.data_arr_producer = data_arr
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://127.0.0.1:5557")
        while len(data_arr) < len(self.numWorkerProcess):
            data_arr.append(None)
        chunk = math.floor(len(data_arr) / len(self.numWorkerProcess))
        modulus = len(data_arr) % len(self.numWorkerProcess)
        firstChunk = modulus + chunk
        sPoint = 0
        while firstChunk <= len(data_arr):
            message = {'array': data_arr[sPoint: firstChunk]}
            zmq_socket.send_json(message)
            if sPoint == 0:
                sPoint = sPoint + firstChunk
            else:
                sPoint = sPoint + chunk
            firstChunk = firstChunk + chunk

    def __consumer(self):
        context = zmq.Context()
        # recieve work
        consumer_receiver = context.socket(zmq.PULL)
        consumer_receiver.connect("tcp://127.0.0.1:5557")
        # send work
        consumer_sender = context.socket(zmq.PUSH)
        consumer_sender.connect("tcp://127.0.0.1:5558")

        while True:
            work = consumer_receiver.recv_json()
            data = work['array']
            consumerResult = self.Map(data)
            r = {'consumerResult': consumerResult}
            consumer_sender.send_json(r)

    def __resultCollector(self):
        context = zmq.Context()
        results_receiver = context.socket(zmq.PULL)
        results_receiver.bind("tcp://127.0.0.1:5558")
        collecter_data = []
        for x in range(len(self.numWorkerProcess)):
            result = results_receiver.recv_json()
            collecter_data.append(result['consumerResult'])

        print("result", self.Reduce(collecter_data), "\n")

    def start(self, data_arr):
        self.pResultCollector = Process(target=self.__resultCollector, )

        for i in range(self.NumWorker):
            pConsumer = Process(target=self.__consumer, )
            pConsumer.start()
            self.numWorkerProcess.append(pConsumer)

        self.pResultCollector.start()

        self.pProducer = Process(target=self.__producer(data_arr), )
        self.pProducer.start()

        self.pResultCollector.join()
        self.pProducer.join()
        for pConsumer in self.numWorkerProcess:
            pConsumer.terminate()
            pConsumer.join()


class FindMax(MapReduce):
    def Map(self, array):
        if None in array:
            return None
        else:
            return max(filter(None, array))

    def Reduce(self, array):
        return max(filter(None, array))


class FindSum(MapReduce):
    def Map(self, array):
        if None in array:
            return None
        else:
            return sum(array)

    def Reduce(self, array):
        return sum(filter(None, array))


class FindNegativeCount(MapReduce):
    def Map(self, array):
        return sum(n < 0 for n in filter(None, array))

    def Reduce(self, array):
        return sum(filter(None, array))


processes = []

map = FindMax(2)
print("Find max called")
map.start([1, 2, -43, 9, 3, 4, 5, 566])

map = FindSum(18)
print("Find sum called")
map.start([1, 2, -43, 9, 5, 3, 4, 5, 566])

map = FindNegativeCount(50)
print("FindNegativeCount called")
map.start([1, 2, 43, -9, -1, -2, -55, 5, 3, 4, 5, 566])
