import math
import random
import zmq
from abc import ABC, abstractmethod
from multiprocessing import Process


class MapReduce(ABC):
    worker_process = []
    process_producer = None
    process_result_collector = None

    def __init__(self, num_worker):
        self.num_worker = num_worker
        self.data_arr_map = None
        self.data_arr_reduce = None
        super().__init__()

    @abstractmethod
    def map(self, data_arr):        # data_arr: Integer Array
        self.data_arr_map = data_arr

    @abstractmethod
    def reduce(self, data_arr):     # data_arr: Integer Array
        self.data_arr_reduce = data_arr

    def __producer(self, data_arr):
        self.data_arr_producer = data_arr
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://127.0.0.1:5557")
        while len(data_arr) < len(self.worker_process):
            data_arr.append(None)
        block = math.floor(len(data_arr) / len(self.worker_process))
        first = block + (len(data_arr) % len(self.worker_process))
        point = 0
        while first <= len(data_arr):
            message = {'array': data_arr[point: first]}
            zmq_socket.send_json(message)
            point = point + first if point == 0 else point + block
            first += block

    def __consumer(self):
        context = zmq.Context()
        consumer_receiver = context.socket(zmq.PULL)        # Receive Work
        consumer_receiver.connect("tcp://127.0.0.1:5557")
        consumer_sender = context.socket(zmq.PUSH)          # Send Work
        consumer_sender.connect("tcp://127.0.0.1:5558")
        while True:
            work = consumer_receiver.recv_json()
            data = work['array']
            consumer_result = self.map(data)
            r = {'consumer_result': consumer_result}
            consumer_sender.send_json(r)

    def __result_collector(self):
        context = zmq.Context()
        results_receiver = context.socket(zmq.PULL)
        results_receiver.bind("tcp://127.0.0.1:5558")
        collector_data = []
        for x in range(len(self.worker_process)):
            result = results_receiver.recv_json()
            collector_data.append(result['consumer_result'])
        print("{} Result: {}".format(str(self.__class__.__name__), self.reduce(collector_data)))

    def start(self, data_arr):                              # data_arr: Integer Array
        self.process_result_collector = Process(target=self.__result_collector, )
        for i in range(self.num_worker):
            process_consumer = Process(target=self.__consumer, )
            process_consumer.start()
            self.worker_process.append(process_consumer)
        self.process_result_collector.start()
        self.process_producer = Process(target=self.__producer(data_arr), )
        self.process_producer.start()
        self.process_result_collector.join()
        self.process_producer.join()
        for process_consumer in self.worker_process:
            process_consumer.terminate()
            process_consumer.join()


class FindMax(MapReduce):
    def __init__(self, num_worker):
        MapReduce.__init__(self, num_worker)

    def map(self, data_arr):
        return None if None in data_arr else max(filter(None, data_arr))

    def reduce(self, data_arr):
        return max(filter(None, data_arr))


class FindSum(MapReduce):
    def __init__(self, num_worker):
        MapReduce.__init__(self, num_worker)

    def map(self, data_arr):
        return None if None in data_arr else sum(data_arr)

    def reduce(self, data_arr):
        return sum(filter(None, data_arr))


class FindNegativeCount(MapReduce):
    def __init__(self, num_worker):
        MapReduce.__init__(self, num_worker)

    def map(self, data_arr):
        return sum(n < 0 for n in filter(None, data_arr))

    def reduce(self, data_arr):
        return sum(filter(None, data_arr))


if __name__ == '__main__':
    def rand(start, end, num):
        res = []
        [res.append(random.randint(start, end)) for _ in range(num)]
        return res

    s = rand(-200, 200, 20)
    print(s)
    map = FindMax(4)
    map.start(s)
    map = FindSum(10)
    map.start(s)
    map = FindNegativeCount(20)
    map.start(s)
