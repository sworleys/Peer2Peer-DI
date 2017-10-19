import socketserver, re, socket, time, datetime
import linked_list

TTL_INIT = 7200

class Peer(linked_list.Node):
    """
    """

    def __init__(self, hostname, cookie, active, ttl, port, num_active, recent_timestamp):
        self._hostname = hostname
        self._cookie = cookie
        self._active = active
        self._ttl = ttl
        self._port = port
        self._num_active = num_active
        self._recent_timestamp = recent_timestamp

    def get_hostname(self):
        return self._hostname

    def get_cookie(self):
        return self._cookie

    def is_active(self):
        return self._active

    def get_ttl(self):
        return self._ttl

    def get_port(self):
        return self._port

    def get_num_active(self):
        return self._num_active

    def get_recent_timestamp(self):
        return self._recent_timestamp

    def set_active(self, flag):
        self._active = flag

    def set_recent_timestamp(self, timestamp):
        self._recent_timestamp = timestamp

    def inc_num_active(self):
        self._num_active += 1

    def equals(self, peer):
        return self._cookie == peer.get_cookie()


class PeerList(linked_list.LinkedList):
    """
    """

    def search(self, cookie):
        current = self.get_head()
        found = False
        while current and not found:
            if current.get_cookie() == cookie:
                found = True
            else:
                current = current.get_next()

        return found

    def active_to_string(self):
        active_str = ""
        current = self.get_head()
        while current:
            print(current.get_hostname())
            if current.is_active():
                active_str += current.get_hostname() + ":" + str(current.get_port()) + "\n"
                print(active_str)

            current = current.get_next()

        return active_str


class RegServer(socketserver.BaseRequestHandler):
    """
    """
    
    peer_list = PeerList()
    cookie_index = 0

    def handle(self):
        self.data = str(self.request.recv(1024).strip(), "utf-8")
        print(self.data)

        m = re.search('Register <sp> (\d+) <cr> <lf>', self.data)

        if m:
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            cookie = self.cookie_index
            self.cookie_index += 1
            active = True
            ttl = TTL_INIT
            port = self.client_address[1]
            num_active = 1
            t_utc = time.time()
            recent_timestamp = datetime.datetime.fromtimestamp(t_utc).strftime("%Y-%m-%d %H:%M:%S")
            peer = Peer(hostname, cookie, active, ttl, port, num_active, recent_timestamp)

            self.peer_list.add_head(peer)
            print(self.peer_list.active_to_string())
            self.request.sendall(self.peer_list.active_to_string().encode("utf-8"))



if __name__ == "__main__":
    try:
        HOST, PORT = "localhost", 65423
        
        #peerList = PeerList()
        #cookie_index = 0

        server = socketserver.TCPServer((HOST, PORT), RegServer)

        server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting...")
        server.shutdown()

