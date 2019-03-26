from abc import ABC, abstractmethod


class MapReduce(ABC):

    def __init__(self, NumWorker):
        self.NumWorker = NumWorker
        self.data_arr_map = None
        self.data_arr_reduce = None
        super().__init__()

    @abstractmethod
    def map(self, data_arr):        # data_arr: Integer Array
        self.data_arr_map = data_arr

    @abstractmethod
    def reduce(self, data_arr):     # data_arr: Integer Array
        self.data_arr_reduce = data_arr

    def __producer(self, data_arr): # data_arr: Integer Array
        pass

    def __consumer(self):
        pass

    def __resultCollector(self):
        pass

    def start(self, data_arr):      # data_arr: Integer Array
        pass
