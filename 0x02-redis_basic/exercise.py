#!/usr/bin/env python3

"""
write to a redis server
"""
import redis
import uuid
from typing import Union, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """counts the number of times a method is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """use the qualified name of the method as the key"""
        key = method.__qualname__
        self._redis.incr(key)
        result = method(self, *args, **kwargs)
        return result
    return wrapper


def call_history(method: Callable) -> Callable:
    """keep tab of inputs and outputs"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """method name"""
        key = method.__qualname__
        inputslist_key = key + ":inputs"
        outputslist_key = key + ":outputs"
        input_str = str(args)
        self._redis.rpush(inputslist_key, input_str)
        output = method(self, *args, **kwargs)
        self._redis.rpush(outputslist_key, str(output))
        return output
    return wrapper


def replay(method: Callable) -> None:
    """display call history of a particular func"""
    cache = redis.Redis()

    method_name = method.__qualname__
    counter = cache.get(method_name).decode('utf-8')
    # retrieve input output list
    inputslist_key = f"{method_name}:inputs"
    outputslist_key = f"{method_name}:outputs"
    inputs_history = cache.lrange(inputslist_key, 0, -1)
    outputs_history = cache.lrange(outputslist_key, 0, -1)
    print(f"{method_name} was called {counter} times")
    # loop through using zip
    for input_str, output_str in zip(inputs_history, outputs_history):
        # Convert byte strings to UTF-8
        input_str = input_str.decode('utf-8')
        output_str = output_str.decode('utf-8')
        print(f"{method_name}(*{input_str}) -> {output_str}")


class Cache():
    """
    connect to redis server and store key-value pairs
    type-annotate store method to reflect that data can be of diff types
    implement system that counts how many times methods of the Cache class
    is called
    """
    def __init__(self):
        """connect to existing redis server, clear all existing keys"""
        self._redis = redis.Redis(host='localhost', port=6379)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """generate random key using uuid, store data as key's value"""
        randkey = str(uuid.uuid4())
        self._redis.set(randkey, data)
        return randkey

    def get(self, key: str, fn: Callable = None
            ) -> Union[str, bytes, int, float]:
        """
        retrieve data from Redis using the key
        if conversion function fn is provided, convert data
        to utf-8 string, return
        if key does not exist, return none
        """
        data = self._redis.get(key)
        if data is not None:
            return fn(data) if fn is not None else data
        else:
            return None

    def get_str(self, key: str) -> str:
        """shortcut func for callaing 'get' with str conversion"""
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """shortcut func for calling 'get' with int conversion"""
        return self.get(key, fn=int)
