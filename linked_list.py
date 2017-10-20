from abc import ABC, abstractmethod

# Node class in LinkedList
class Node(ABC):
    """
    """
    # variable to hold next node in list
    __next = None

    # Constructor : creates Node object and sets data field
    # @param data: holds data of node
    @abstractmethod
    def __init__(self, data):
        pass

    # Returns next node
    # @return next node in list
    def get_next(self):
        return self.__next

    # Sets next node in the list
    # @param newNext: next node in list
    def set_next(self, newNext):
        self.__next = newNext

    # returns true if specified node is equal
    # @param node: given node to check if it is equal
    @abstractmethod
    def equals(self, node):
        return

# LinkedList class
class LinkedList(ABC):
    """
    """

    # Constructor: sets head of list to none
    def __init__(self):
        self.__head = None

    # Tells if LinkedList is empty
    # @return turn if list is empty
    def is_empty(self):
        return self.__head == None

    # Returns head of the LinkedList
    # @return head node of list
    def get_head(self):
        return self.__head

    # Sets the head of the list with the given node
    # @param given node to be head of the list
    def add_head(self, node):
        node.set_next(self.__head)
        self.__head = node

    # Returns size of the list
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

