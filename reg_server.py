import socketserver, re, socket, time, datetime, threading, sys
import linked_list


__author__ = "Stephen Worley"
__credits__ = ["Stephen Worley", "Louis Le"]
__license__ = "GPL"
__maintainer__ = "Stephen Worley"
__email__ = "sworley1995@gmail.com"
__status__ = "Development"


# Initial value of a ttl
TTL_INIT = 7200

# Global peer list
_peer_list = PeerList()

# Global value for keeping track of used cookies
_cookie_index = 0



class Peer(linked_list.Node):
    """Node in the linked list

    """

    def __init__(self, hostname, cookie, active, ttl, port, num_active, recent_timestamp):
        """Peer Constructor

        """
        # hostname of peer server
        self._hostname = hostname
        # cookie assigned to peer
        self._cookie = cookie
        # active flag, expires according to leave or ttl
        self._active = active
        # Time to Live value, initially 7200 seconds
        self._ttl = ttl
        # port used by peer server
        self._port = port
        # number of times active
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


    def set_active(self):
        self._active = True

    def set_inactive(self):
        self._active = False


    def set_recent_timestamp(self, timestamp):
        self._recent_timestamp = timestamp


    def inc_num_active(self):
        """Increments the number of times the Peer
        has been active by 1

        """

        self._num_active += 1


    def equals(self, peer):
        """Checks if Peer equals Peer based on cookie

        """

        return self._cookie == peer.get_cookie()


    def refresh(self):
        """Resets the ttl field, marks it as active,
        and sets new recent timestamp for Peer

        """

        self._recent_timestamp = datetime.datetime.fromtimestamp(\
                time.time()).strftime("%Y-%m-%d %H:%M:%S")
        self._ttl = TTL_INIT
        self.set_active()


    def decrement_ttl(self):
        """Decrements the ttl field by 1 if it is not
        already 0

        """

        if (self._ttl > 0):
            self._ttl -= 1


class PeerList(linked_list.LinkedList):
    """Linked list for Peers that have registered

    """

    def search(self, cookie):
        """Searches for Peer in the list based on cookie

        """

        current = self.get_head()
        while current:
            if current.get_cookie() == cookie:
                return True
            else:
                current = current.get_next()

        return False


    def search_host(self, hostname, port):
        """Searches for Peer in the list based on hostname

        """

        current = self.get_head()
        while current:
            if (current.get_hostname() == hostname) and (current.get_port() == port):
                return True
            else:
                current = current.get_next()

        return False


    def get_peer(self, cookie):
        """Gets the Peer from the list based on cookie

        """

        current = self.get_head()
        while current:
            if (current.get_cookie() == cookie):
                return current
            else:
                current = current.get_next()


    def active_to_string(self):
        """Loops through list and returns a string of every
        Peer marked active along with there port number

        """

        active_str = ""
        current = self.get_head()
        while current:
            if current.is_active():
                active_str += current.get_hostname() + ":" + str(current.get_port()) + "\n"

            current = current.get_next()

        return active_str


    def decrement_ttls(self):
        """Loops through list and decrements the ttls
        of every Peer marked active

        """

        current = self.get_head()
        while current:
            if current.is_active():
                current.decrement_ttl()
            if (current.get_ttl() == 0):
                current.set_inactive()

            current = current.get_next()




class RegServer(socketserver.BaseRequestHandler):
    """Request Handler for the Registration Server

    """


    def handle(self):
        """Implemented handle method

        """

        global _peer_list
        global _cookie_index
        self.data = str(self.request.recv(1024).strip(), "utf-8")

        register = re.search('Register: (\d+)', self.data)
        p_query = re.search('PQuery', self.data)
        keep_alive = re.search('KeepAlive: (\d+)', self.data)
        leave = re.search('Leave: (\d+)', self.data)

        #TODO: Keep track in num_active the number of times it has been active in the last 30 days
        #TODO: Honestly, should add toString method to test all this on close
        if register:
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            port = register.group(1)

            if _peer_list.search_host(hostname, port):
                self.request.sendall("Already Registered".encode("utf8"))
            else:
                #TODO: I think that when a ttl expires it should lose the cookie?
                cookie = _cookie_index
                _cookie_index += 1
                active = True
                ttl = TTL_INIT
                num_active = 1
                t_utc = time.time()
                recent_timestamp = datetime.datetime.fromtimestamp(t_utc).strftime("%Y-%m-%d %H:%M:%S")
                peer = Peer(hostname, cookie, active, ttl, port, num_active, recent_timestamp)
                _peer_list.add_head(peer)
                self.request.sendall(str(cookie).encode("utf8"))

        #TODO: Add ttl refresh for query
        elif p_query:
            self.request.sendall(_peer_list.active_to_string().encode("utf-8"))

        elif keep_alive:
            peer = _peer_list.get_peer(int(keep_alive.group(1)))
            if peer:
                peer.refresh()
                self.request.sendall("Refreshed".encode("utf8"))
            else:
                self.request.sendall("Peer not found".encode("utf8"))

        elif leave:
            peer = _peer_list.get_peer(int(leave.group(1)))
            if peer:
                peer.set_inactive()
                self.request.sendall("Left".encode("utf8"))
            else:
                self.request.sendall("Peer not found".encode("utf8"))

        else:
            self.request.sendall("Error in Request".encode("utf8"))



def ticker(e, peer_list):
    """Second-based ticker for decrementing ttls
    every second

    """

    while(e.isSet()):
        time.sleep(1)
        peer_list.decrement_ttls()


if __name__ == "__main__":

    e = threading.Event()

    try:
        HOST, PORT = "localhost", 65423
        

        server = socketserver.TCPServer((HOST, PORT), RegServer)

        e.set()

        # Start ticker as background thread
        t1 = threading.Thread(target=ticker, args=(e, _peer_list))
        t1.start()


        server.serve_forever()


    except(KeyboardInterrupt, SystemExit):
        print("Exiting...")
        e.clear()
        server.shutdown()
        sys.exit()

