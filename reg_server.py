import socketserver, re, socket, time, datetime, threading, sys, queue
from random import randint
import linked_list


__author__ = "Stephen Worley"
__credits__ = ["Stephen Worley", "Louis Le"]
__license__ = "GPL"
__maintainer__ = "Stephen Worley"
__email__ = "sworley1995@gmail.com"
__status__ = "Development"



# Initial value of a ttl
TTL_INIT = 7200

# Seconds in a day
DAY_SECONDS = 86400

# Total number of days to track
DAY_TOTAL = 30

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
        # most recent timestamp
        self._recent_timestamp = recent_timestamp
        # Queue for keeping track of last thirty days active
        self._day_q = queue.Queue(DAY_TOTAL)


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


    def get_day_q(self):
        return self._day_q


    def get_total_active(self):
        """Sums total active of last 30 days
        """

        total = 0
        tmp_q = queue.Queue(DAY_TOTAL)

        for i in range(0, self._day_q.qsize()):
            num_active = self._day_q.get()
            total += num_active
            tmp_q.put(num_active)

        self._day_q = tmp_q
        return total


    def update_day_q(self):
        """
        Adds number of times active from that day to queue
        that keeps track of it for 30 days

        """

        if (self._day_q.qsize() == DAY_TOTAL):
            self._day_q.get()
            self._day_q.put(self._num_active)
        else:
            self._day_q.put(self._num_active)


        self._num_active = 0


    def set_active(self):
        self._active = True

    def set_inactive(self):
        self._active = False


    def set_recent_timestamp(self, timestamp):
        self._recent_timestamp = timestamp


    def set_num_active(self, num):
        self._num_active = num


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


    def get_host(self, hostname, port):
        """Gets the Peer in the list based on hostname

        """

        current = self.get_head()
        while current:
            if (current.get_hostname() == hostname) and (current.get_port() == port):
                return current
            else:
                current = current.get_next()

        return current


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


    def update_active_day(self):
        """Loops through list and updates the 30 day queue

        """

        current = self.get_head()
        while current:
            current.update_day_q()
            current = current.get_next()


    def to_string(self):
        """Loops through list and returns a string

        """

        peer_list_str = ""
        current = self.get_head()
        while current:
            peer_list_str += current.get_hostname() + ":" "\n\t" \
                    + str(current.get_port()) + "\n\t" \
                    + str(current.get_cookie()) + "\n\t" \
                    + str(current.is_active()) + "\n\t" \
                    + str(current.get_ttl()) + "\n\t" \
                    + current.get_recent_timestamp() + "\n\t" \
                    + "num:   " + str(current.get_num_active()) + "\n\t" \
                    + "size:  " + str(current.get_day_q().qsize()) + "\n\t" \
                    + "total: " + str(current.get_total_active()) + "\n\n"

            current = current.get_next()

        return peer_list_str




# Global peer list
_peer_list = PeerList()



class RegServer(socketserver.BaseRequestHandler):
    """Request Handler for the Registration Server

    """


    def handle(self):
        """Implemented handle method

        """

        global _peer_list
        global _cookie_index
        self.data = str(self.request.recv(1024).strip(), "utf-8")
        print(self.data)
        register = re.search('Register: (\d+)', self.data)
        p_query = re.search('PQuery', self.data)
        keep_alive = re.search('KeepAlive: (\d+)', self.data)
        leave = re.search('Leave: (\d+)', self.data)

        if register:
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            port = register.group(1)

            peer = _peer_list.get_host(hostname, port)

            if peer:
                peer.set_active()
                peer.inc_num_active()
                self.request.sendall(("Already Registered with cookie: " \
                        + str(peer.get_cookie())).encode("utf8"))

            else:
                # TODO: I think that when a ttl expires it should lose the cookie?
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

        elif p_query:
            self.request.sendall(_peer_list.active_to_string().encode("utf-8"))

        elif keep_alive:
            peer = _peer_list.get_peer(int(keep_alive.group(1)))
            if peer:
                peer.refresh()
                peer.inc_num_active()
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

    # Second counter
    total_sec = 0

    while(e.isSet()):
        time.sleep(1)
        total_sec += 1
        peer_list.decrement_ttls()

        # Every day run the 30 day
        if (total_sec == DAY_SECONDS):
            # Debugger
            peer = peer_list.get_head()
            if peer:
                peer.set_num_active(randint(0, 100))
            peer_list.update_active_day()
            total_sec = 0



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
        print("Exiting...\n\n")
        e.clear()
        server.shutdown()
        sys.exit()

