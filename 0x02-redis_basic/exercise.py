#!/usr/bin/env python3

"""
write to a redis server
"""
import redis
import uuid


class Cache():
    """
    connect to redis server and store key-value pairs
    """
    def __init__(self):
        """connect to existing redis server, clear all existing keys"""
        self._redis = redis.Redis(host='localhost', port=6379)
        self._redis.flushdb()

    def store(self, data) -> str:
        """generate random key using uuid, store data as key's value"""
        randkey = str(uuid.uuid4())
        self._redis. set(randkey, data)
        return randkey
