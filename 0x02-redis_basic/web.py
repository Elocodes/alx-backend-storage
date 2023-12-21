#!/usr/bin/env python3
"""
script
"""
import requests
import redis
from functools import wraps
import time

# Create a Redis connection
redis_conn = redis.Redis()


def get_page(url: str) -> str:
    """Get HTML content of a URL with caching and access count."""
    # Create a key for counting URL accesses
    count_key = f"count:{url}"

    # Check if the URL access count key exists
    if redis_conn.exists(count_key):
        # Increment the count
        access_count = redis_conn.incr(count_key)
    else:
        # If key doesn't exist, set count to 1
        access_count = redis_conn.set(count_key, 1)

    # Check if the HTML content is cached
    cached_content = redis_conn.get(url)
    if cached_content:
        print(f"URL '{url}' accessed {access_count} times.
              Returning cached content.")
        return cached_content.decode('utf-8')

    # Make a request to the URL
    response = requests.get(url)

    # Cache the HTML content with a 10-second expiration time
    redis_conn.setex(url, 10, response.text)

    print(f"URL '{url}' accessed {access_count} times. Caching content.")
    return response.text


# Bonus: Decorator implementation
def cache_and_count_access(func):
    """count access"""
    @wraps(func)
    def wrapper(url):
        """methods"""
        count_key = f"count:{url}"

        # Increment the count
        access_count = redis_conn.incr(count_key)

        # Check if the HTML content is cached
        cached_content = redis_conn.get(url)
        if cached_content:
            print(f"URL '{url}' accessed {access_count} times.
                  Returning cached content.")
            return cached_content.decode('utf-8')

        # Call the original function
        content = func(url)

        # Cache the HTML content with a 10-second expiration time
        redis_conn.setex(url, 10, content)

        print(f"URL '{url}' accessed {access_count} times. Caching content.")
        return content

    return wrapper


@cache_and_count_access
def get_page_with_decorator(url: str) -> str:
    """Get HTML content of a URL with caching and access using a decorator."""
    # Make a request to the URL
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    # Example usage of get_page function
    slow_url = "http://slowwly.robertomurray.co.uk"
    content = get_page(slow_url)
    print(content)

    # Example usage of get_page_with_decorator function
    fast_url = "http://www.google.com"
    decorated_content = get_page_with_decorator(fast_url)
    print(decorated_content)
