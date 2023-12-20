#!/usr/bin/env python3

"""
write to a redis server
"""
import redis
import uuid
from typing import Union, Callable


class Cache():
    """
    connect to redis server and store key-value pairs
    type-annotate store method to reflect that data can be of diff types
    """
    def __init__(self):
        """connect to existing redis server, clear all existing keys"""
        self._redis = redis.Redis(host='localhost', port=6379)
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """generate random key using uuid, store data as key's value"""
        randkey = str(uuid.uuid4())
        self._redis. set(randkey, data)
        return randkey

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes, int, float]:
        """
        retrieve data from Redis using the key
        if conversion function fn is provided, convert data to utf-8 string, return
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
