import socketserver, re, socket, time, datetime, threading, sys
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


    def refresh(self):
        self._recent_timestamp = datetime.datetime.fromtimestamp(\
                time.time()).strftime("%Y-%m-%d %H:%M:%S")
        self._ttl = TTL_INIT


    def decrement_ttl(self):
        self._ttl -= 1


class PeerList(linked_list.LinkedList):
    """
    """

    def search(self, cookie):
        current = self.get_head()
        while current:
            if current.get_cookie() == cookie:
                return True
            else:
                current = current.get_next()

        return False


    def get_peer(self, cookie):
        current = self.get_head()
        while current:
            print(current.get_cookie())
            print("cookie: " + cookie)
            if (current.get_cookie() == cookie):
                print('DOOF')
                return current
            else:
                current = current.get_next()


    def active_to_string(self):
        active_str = ""
        current = self.get_head()
        while current:
            if current.is_active():
                active_str += current.get_hostname() + ":" + str(current.get_port()) + "\n"

            current = current.get_next()

        return active_str


    def decrement_ttls(self):
        current = self.get_head()
        while current:
            if current.is_active():
                current.decrement_ttl()

            current = current.get_next()


class RegServer(socketserver.BaseRequestHandler):
    """
    """
    
    peer_list = PeerList()
    cookie_index = 0

    def handle(self):
        self.data = str(self.request.recv(1024).strip(), "utf-8")

        register = re.search('Register: (\d+)', self.data)
        p_query = re.search('PQuery', self.data)
        keep_alive = re.search('KeepAlive: (\d+)', self.data)

    # Need to add check here for if already registered
        if register:
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            cookie = self.cookie_index
            self.cookie_index += 1
            active = True
            ttl = TTL_INIT
            port = register.group(1)
            num_active = 1
            t_utc = time.time()
            recent_timestamp = datetime.datetime.fromtimestamp(t_utc).strftime("%Y-%m-%d %H:%M:%S")
            peer = Peer(hostname, cookie, active, ttl, port, num_active, recent_timestamp)
            self.peer_list.add_head(peer)
            self.request.sendall(str(cookie).encode("utf8"))

        elif p_query:
            self.request.sendall(self.peer_list.active_to_string().encode("utf-8"))

        elif keep_alive:
            peer = self.peer_list.get_peer(keep_alive.group(1))
            if peer:
                print(peer.get_ttl)
                peer.refresh()


def ticker(e, peer_list):
    """
    """

    while(e.isSet()):
        peer_list.decrement_ttls()


if __name__ == "__main__":

    e = threading.Event()
    try:
        HOST, PORT = "localhost", 65423
        
        #peerList = PeerList()
        #cookie_index = 0

        server = socketserver.TCPServer((HOST, PORT), RegServer)

        server.serve_forever()

        e.set()
        t1 = threading.Thread(name='non-blocking', target=ticker, args=(e, server.peer_list))
        t1.start()


    except(KeyboardInterrupt, SystemExit):
        print("Exiting...")
        e.clear()
        server.shutdown()
        sys.exit()

