import socketserver, re, socket, time, datetime, threading, sys, os

TTL_INIT = 7200
LOCATION = ""
HOST = ""
PORT = 0
REG_PORT = 65423
REG_HOST = "localhost"
COOKIE = -1
ttl = 0

# Create empty dict
_index_dict = {}

class RFCIndex():
    """
    """

    """
    Constructor: sets class instances to given values
    :param num: RFC number
    :param title: title of RFC file
    :param hostname: hostname of peer that has RFC file
    :param ttl: RFC file time to live
    """
    def __init__(self, num, title, hostname, port, ttl):
        self._num = num
        self._title = title
        self._hostname = hostname
        self._port = port
        self._ttl = ttl

    def get_num(self):
        return self._num

    def get_title(self):
        return self._title

    def get_hostname(self):
        return self._hostname

    def get_ttl(self):
        return self._ttl

    def get_port(self):
        return self._port

    def decrement_ttl(self):
        self._ttl -= 1

    def refresh(self):
        self._ttl = TTL_INIT

    def __str__(self):
        return str(self._num) + "|" + self._title + "|" + self._hostname + "|" + str(self._ttl)


class RFCServer(socketserver.BaseRequestHandler):
    """
    """

    def handle(self):
        global _peer_list
        global _cookie_index
        self.data = str(self.request.recv(1024).strip(), "utf-8")
        # Number is port number
        rfc_query = re.search('RFCQuery: (\d+)', self.data)
        # Numbers are port number and RFC number 
        get_rfc = re.search('GetRFC: (\d+) (\d+)', self.data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # A peer requests the RFC index from a remote peer.
        if rfc_query:
            print("RFC Query Received")
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            port = rfc_query.group(1)
            
            try:
                sock.connect((hostname, port))
                # Converts dict to string separated by newline delimiter
                data = ''
                for key, value in _index_dict.items():
                    data += str(value) + '\n'  
                # Sends over string 
                sock.sendall(bytes(data, "utf-8"))

                recieved = str(sock.recv(1024), "utf-8")

            finally:
                sock.close()
            print("RFC Query Sent")

        # A peer requests to download a specific RFC document from a remote peer.
        elif get_rfc:
            print("RFC File Request")
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            port = get_rfc.group(1)
            rfc_num = get_rfc.group(2)

            try:
                sock.connect((hostname, port))
                # Converts file to string
                data = open(LOCATION + rfc_num + '.txt', 'r').read()
                # Sends over string
                sock.sendall(bytes(data, "utf-8"))

                recieved = str(sock.recv(1024), "utf-8")

            finally:
                sock.close()
            print("RFC File Sent")

def merge(data):
    for index in data.split("\n"):
        split_index = index.split("|")

        num = split_index[0]
        title = split_index[1]
        hostname = split_index[2]
        port = split_index[3]
        ttl = split_index[4]     

        key = num + "_" + hostname + "_" + port

        if not(key in _index_dict):
            rfc = RFCIndex(num, title, hostname, ttl)
            _index_dict[key] = rfc 

"""
Finds the title for a given RFC file
:param fil: file name/location, fil because file is a reserved word for python
:returns: title of the given RFC file
"""
def getTitle(fil):
    f = open(fil, 'r') #opens file
    counter = 0 # Used to keep track of position in RFC file
    title = "" # Title of RFC file
    for line in f:
        # When counter is 0, it will skip all the first few blank lines
        # When counter is 1, it will skip the header info lines
        # When counter is 2, it will skip the empty lines before the title
        if (counter == 0 and line != "\n") or \
            (counter == 1 and line == "\n") or \
            (counter == 2 and line != "\n"):
            counter += 1
        # Once it is 3, it wil copy all lines until it hits another empty line
        if counter == 3:
            if line != "\n":
                # trims excess spaces and gets rid of break lines
                title += line.strip(' ').replace('\n','')
            else:
                break
    f.close()
    return title

def ticker(e, index_dict):
    """
    """
    global ttl

    while(e.isSet()):
        time.sleep(1)
        if ttl > 0:
            ttl -= 1
        if ttl <= 10 and ttl >= 1:
            keep_aliveB()
        for key, value in _index_dict.items():
            key_split = key.split("_")
            if not(key_split[1] == HOST and key_split[2] == PORT):
                value.decrement_ttl()
                if value.get_ttl() == 0:
                    _index_dict.pop(key)

def regis():
    global ttl, COOKIE
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((REG_HOST, REG_PORT))
        ttl = TTL_INIT
        sock.sendall(bytes("Register: " + str(PORT), "utf-8"))

        COOKIE = str(sock.recv(1024), "utf-8")
        print("Peer recieved.")
    finally:
        sock.close()

def keep_aliveB():
    global ttl
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command = "KeepAlive: " + str(COOKIE)
    try:
        sock.connect((REG_HOST, REG_PORT))
        sock.sendall(bytes(command, "utf-8"))

        recieved = str(sock.recv(1024), "utf-8")
        print(recieved)
    finally:
        sock.close()
    ttl = TTL_INIT

def leaveB():
    global ttl
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((REG_HOST, REG_PORT))
        sock.sendall(bytes("Leave: " + str(PORT), "utf-8"))

        recieved = str(sock.recv(1024), "utf-8")
        print(recieved)
    finally:
        sock.close()
    ttl = 0

def p_query():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recieved = ""
    try:
        sock.connect((REG_HOST, REG_PORT))
        sock.sendall(bytes(command, "utf-8"))

        # receives list of active peers
        recieved = str(sock.recv(1024), "utf-8")
    finally:
        sock.close()

    print(recieved)
    data = recieved.split("\n")
    return data

def rfc_query(hostname, port):
    global PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((hostname, port))
        sock.sendall(bytes("RFCQuery: " + PORT, "utf-8"))

        recieved = str(sock.recv(1024), "utf-8")
        merge(recieved)
    finally:
        sock.close()

def get_rfc(hostname, port):
    global LOCATIOn
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        fil = LOCATION + num + ".txt"

        sock.connect((host, portname))
        sock.sendall(bytes(command, "utf-8"))

        recieved = str(sock.recv(1024), "utf-8")
        f = open(fil, "w+")
        f.write(recieved)
        f.close()

        key = num + "_" + hostname + "_" + port
        if not(key in _index_dict):
            rfc = RFCIndex(num, getTitle(fil), hostname, port, TTL_INIT)
            _index_dict[key] = rfc
    finally:
        sock.close()

def search(num):
    return {k:v for k,v in _index_dict.items() if k.startswith(num)}

def user_input(e):
    """
    """

    while(e.isSet()):
        command = input("Enter command: ")

        register = re.search('Register', command)
        p_query = re.search('PQuery', command)
        keep_alive = re.search('KeepAlive', command)
        leave = re.search('Leave', command)
        # Numbers are hostname and port number
        rfc_query = re.search('RFCQuery: ([a-z,0-9,.,-]+) (\d+)', command)
        # Numbers are hostname, port number and RFC number
        get_rfc = re.search('GetRFC: ([a-z,0-9,.,-]+) (\d+) (\d+)', command) 
        find = re.search('Search: (\d+)', command)
        if register:
            regis()
        elif keep_alive:
            keep_aliveB()
        elif leave:
            leaveB()
        elif p_query:
            p_query()
        elif rfc_query:
            hostname = rfc_query.group(1)
            port = rfc_query.group(2)
            data = rfc_query(hostname, port)
            print(data)
        elif get_rfc:
            hostname = get_rfc.group(1)
            port = get_rfc.group(2)
            num = get_rfc.group(3)
            get_rfc(hostname, port, num)
        elif find:
            found = False
            num = find.group(1)
            temp_index = search(num)
            if not temp_index:
                data = p_query('PQuery')
                for d in data:
                    peer = d.split(":")
                    hostname = peer[0]
                    port = peer[1]
                    rfc_query(hostname, port)
                    temp_index = search(num)
                    if temp_index:
                        get_rfc(temp_index[0].get_hostname, temp_index.get_port, num)
                        found = True
                        break
                if not found:
                    print("RFC not in P2P network.\n")
            else:
                if (num + "_" + hostname + "_" + port) in temp_index:
                    print("Already in this peer.\n")
                else:
                    get_rfc(temp_index.get_hostname, temp_index.get_port, num)
                    found = True
            if found:
                print("RFC downloaded.")


if __name__ == "__main__":

    e = threading.Event()
    try:
        # Sets values based on user input from command-line
        HOST, LOCATION, PORT = sys.argv[1], sys.argv[2], int(sys.argv[3])
        
        # Error check in case user didn't include / at end of location
        if(LOCATION[-1] != "/"):
            LOCATION += "/"

        server = socketserver.TCPServer((HOST, PORT), RFCServer)
        print(server)

        # Loops through all files to add them to the dictionary by RFC number
        for root, dirs, filenames in os.walk(LOCATION):
            for f in filenames:
                rfc_num = f[:-4] # removes .txt part of filename 
                rfc = RFCIndex(rfc_num, getTitle(LOCATION + f), HOST, PORT, TTL_INIT)
                _index_dict[str(rfc_num) + "_" + HOST + "_" + str(PORT)] = rfc

        e.set()
        # Thread for decrementing TTL for RFC indexes
        t1 = threading.Thread(target=ticker, args=(e, _index_dict))
        print(t1)
        t1.start()
        # Thread for taking user input
        t2 = threading.Thread(target=user_input, args=(e,))
        print(t2)
        t2.start()

        server.serve_forever()

    except(KeyboardInterrupt, SystemExit):
        print("Exiting...")

        e.clear()
        server.shutdown()
        sys.exit()

