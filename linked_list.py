from abc import ABC, abstractmethod

__author__ = "Stephen Wolrey, Louis Le"
__credits__ = ["Stephen Worley, Louis Le"]
__license__ = "GPL"
__maintainer__ = "Stephen Worley"
__email__ = "sworley1995@gmail.com"
__status__ = "Development"


class Node(ABC):
    """Abstract Node Class

    """
    # variable to hold next node in list
    _next = None

    @abstractmethod
    def __init__(self, data):
        pass


    def get_next(self):
        """Return next Node in list

        """

        return self._next


    def set_next(self, newNext):
        """Set next Node in list

        """

        self._next = newNext



class LinkedList(ABC):
    """Linked List Class

    """

    def __init__(self):
        """Linked List Constructor

        """

        self._head = None


    def is_empty(self):
        """Checks if list is empty

        """

        return self._head == None


    def get_head(self):
        """Returns head of list

        """

        return self._head


    def add_head(self, node):
        """Add Node to head of list

        """

        node.set_next(self._head)
        self._head = node


    def size(self):
        """Calculates the size of the list

        """

        count = 0
        current = self._head
        while current:
            count += 1
            current = current.get_next()

        return count


    @abstractmethod
    def search(self, item):
        return

