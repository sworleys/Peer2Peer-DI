from abc import ABC, abstractmethod


class Node(ABC):
    """
    """

    __next = None

    @abstractmethod
    def __init__(self, data):
        pass

    def get_next(self):
        return self.__next

    def set_next(self, newNext):
        self.__next = newNext

    @abstractmethod
    def equals(self, node):
        return


class LinkedList(ABC):
    """
    """

    def __init__(self):
        self.__head = None

    def is_empty(self):
        return self.__head == None

    def get_head(self):
        return self.__head

    def add_head(self, node):
        node.set_next(self.__head)
        self.__head = node

    def size(self):
        count = 0
        current = self.__head
        while current:
            count += 1
            current = current.get_next()

        return count

    @abstractmethod
    def search(self, item):
        return

