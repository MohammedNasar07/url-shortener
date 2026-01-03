# cache.py
from collections import OrderedDict


class LRUCache:
    """
    Least Recently Used (LRU) cache.
    - get(key): O(1), returns value or None; moves key to most-recent position.
    - put(key, value): O(1), inserts/updates; evicts oldest when capacity exceeded.
    """

    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def size(self) -> int:
        return len(self.cache)
