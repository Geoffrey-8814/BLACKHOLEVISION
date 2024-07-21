import multiprocessing as mp
import time
import numpy as np
import ctypes

class SharedArray:
    def __init__(self, shape, dtype=ctypes.c_double):
        self.shape = shape
        self.dtype = dtype
        self.size = int(np.prod(shape))
        self.array = mp.Array(dtype, self.size)
        self.lock = mp.Lock()

    def put(self, data):
        with self.lock:
            shared_array = np.frombuffer(self.array.get_obj(), dtype=self.dtype).reshape(self.shape)
            np.copyto(shared_array, data)

    def get(self):
        with self.lock:
            shared_array = np.frombuffer(self.array.get_obj(), dtype=self.dtype).reshape(self.shape)
            return shared_array.copy()
        
class SharedValue:
    def __init__(self, dtype=ctypes.c_double):
        self.value = mp.Value(dtype, 0)
        self.lock = mp.Lock()

    def set(self, data):
        with self.lock:
            self.value.value = data

    def get(self):
        with self.lock:
            return self.value.value