import socketserver
import linked_list


class Peer(linked_list.Node):
    """
    """

    def __init__(self, hostname, cookie, active, ttl, port, num_active, recent_timestamp):
        self.__hostname = hostname
        self.__cookie = cookie
        self.__active = active
        self.__ttl = ttl
        self.__port = port
        self.__num_active = num_active
        self.__recent_timestamp = recent_timestamp

    def get_hostname(self):
        return self.__hostname

    def get_cookie(self):
        return self.__cookie

    def is_active(self):
        return self.__active

    def get_ttl(self):
        return self.__ttl

    def get_port(self):
        return self.__port

    def get_num_active(self):
        return self.__num_active

    def get_recent_timestamp(self):
        return self.__recent_timestamp

    def set_active(self, flag):
        self.__active = flag

    def set_recent_timestamp(self, timestamp):
        self.__recent_timestamp = timestamp

    def inc_num_active(self):
        self.__num_active += 1

    def equals(self, peer):
        return self.__cookie == peer.get_cookie()


class PeerList(linked_list.LinkedList):
    """
    """

    def search(self, cookie):
        current = self.head
        found = False
        while current and not found:
            if current.get_cookie() == cookie:
                found = True
            else:
                current = current.get_next()

        return found

    def active_to_string(self):
        active_str = ""
        current = self.head
        while current:
            if current.is_active():
                active_str.join([current.get_hostname(), ":", str(current.get_port(), "\n")])

        return active_str


class RegServer(socketserver.BaseRequestHandler):
    """
    """

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        self.request.sendall(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = "localhost", 65423

    server = socketserver.TCPServer((HOST, PORT), RegServer)

    server.serve_forever()
   
