import socketserver, re, socket, time, datetime, threading, sys, os, time, itertools, os.path, random

TTL_INIT = 7200
LOCATION = ""
HOST = ""
PORT = 0
REG_PORT = 65423
# REG_HOST = "192.168.0.73"
REG_HOST = "localhost"
COOKIE = -1
ttl = 0
total_time = 0
file_counter = 0
sinT_name = ""
totT_name = ""

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
        self._ttl = int(ttl)

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
        return str(self._num) + "|" + self._title + "|" + self._hostname + "|" + str(self._port) + "|" + str(self._ttl)


class ThreadedRFCServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class RFCServer(socketserver.BaseRequestHandler):
    """
    """

    def handle(self):
        global _peer_list
        global _cookie_index
        LENGTH = 1024
        self.data = str(self.request.recv(1024).strip(), "utf-8")
        print(self.data)
        # Number is port number
        rfc_query = re.search('RFCQuery: (\d+)', self.data)
        # Numbers are port number and RFC number 
        get_rfc = re.search('GetRFC: (\d+) (\d+)', self.data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # A peer requests the RFC index from a remote peer.
        if rfc_query:
            #print("\nRFC Query Request")
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            port = rfc_query.group(1)
            
            data = ''

            for key, value in _index_dict.items():
                data += str(value) + '`'
            data = data[:-1]

            size = len(data)

            self.request.sendall(str(size).encode("utf8"))

            while size > 0:
                size -= LENGTH
                self.request.sendall((data[:1024]).encode("utf8"))
                data = data[1024:]            
            
            #print("\nRFC Query Sent\n\nEnter command: ")

        # A peer requests to download a specific RFC document from a remote peer.
        elif get_rfc:
            #print("\nRFC File Request")
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            port = get_rfc.group(1)
            rfc_num = get_rfc.group(2)

            
            if os.path.isfile(LOCATION + str(rfc_num) + '.txt'):
                data = open(LOCATION + str(rfc_num) + '.txt', 'r').read()

                size = len(data)

                self.request.sendall(str(size).encode("utf8"))

                while size > 0:
                    size -= LENGTH
                    self.request.sendall((data[:1024]).encode("utf8"))
                    data = data[1024:]

                #print("\nRFC File Sent: " + str(rfc_num) + "\n\nEnter command: ")
            else: 
                self.request.sendall("RFC File Not Found".encode("utf8"))
                print("\nRFC File Not Found: " + str(rfc_num) + "\n\nEnter command: ")
            

def merge(data):
    for index in data.split("`"):
        if(len(index) == 0):
            continue
        split_index = index.split("|")
        num = split_index[0]
        title = split_index[1]
        hostname = split_index[2]
        port = split_index[3]
        ttl = split_index[4]     

        key = num + "_" + hostname + "_" + port

        if not(key in _index_dict):
            rfc = RFCIndex(num, title, hostname, port, ttl)
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
    global ttl, COOKIE, REG_HOST, REG_PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((REG_HOST, REG_PORT))
        ttl = TTL_INIT
        sock.sendall(bytes("Register: " + str(PORT), "utf-8"))

        COOKIE = str(sock.recv(1024), "utf-8")
        print("Peer recieved.")
        print("Cookie: " + COOKIE)
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
        sock.sendall(bytes("Leave: " + str(COOKIE), "utf-8"))

        recieved = str(sock.recv(1024), "utf-8")
        print(recieved)
    finally:
        sock.close()
    ttl = 0

def p_queri():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recieved = ""
    try:
        sock.connect((REG_HOST, REG_PORT))
        sock.sendall(bytes("PQuery", "utf-8"))

        # receives list of active peers
        recieved = str(sock.recv(1024), "utf-8")
    finally:
        sock.close()

    print(recieved)

    if len(recieved) > 0 and recieved[-1] == "\n":
        recieved =recieved[:-1]
    data = recieved.split("\n")
    return data

def rfc_queri(hostname, port):
    global PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp = ""
    recieved = ""

    size = 0

    try:
        sock.connect((hostname, int(port)))
        sock.sendall(bytes("RFCQuery: " + str(PORT), "utf-8"))

        first_rec = str(sock.recv(1024), "utf-8")
        print(first_rec)

        try:
            size = int(first_rec)
        except ValueError:
            pos = first_rec.find("\n")
            size = int("".join(itertools.takewhile(str.isdigit, first_rec)))
            recieved += first_rec[len(str(size)):]
        while size > 0:
            temp = str(sock.recv(1024), "utf-8")
            recieved += temp
            size -= 1024

        merge(recieved)
    finally:
        sock.close()

def git_rfc(hostname, port, num):
    
    start_time = time.time()
    global LOCATION, file_counter, total_time
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        fil = LOCATION + str(num) + ".txt"
        recieved = ""
        temp = ""

        sock.connect((hostname, int(port)))
        sock.sendall(bytes("GetRFC: " + str(port) + " " + str(num), "utf-8"))

        first_rec = str(sock.recv(1024), "utf-8")

        print(first_rec)

        not_found = re.search("RFC File Not Found", first_rec)

        if not_found:
            print("RFC File Not Found: " + str(num))
            sock.close()
            return

        try:
            size = int(first_rec)
        except ValueError:
            pos = first_rec.find("\n")
            size = int("".join(itertools.takewhile(str.isdigit, first_rec)))
            recieved += first_rec[len(str(size)):]
        while size > 0:
            temp = str(sock.recv(1024), "utf-8")
            print(temp)
            recieved += temp
            size -= 1024
        f = open(fil, "w+")
        f.write(recieved)
        f.close()

        key = str(num) + "_" + hostname + "_" + str(port)
        if not(key in _index_dict):
            rfc = RFCIndex(num, getTitle(fil), hostname, int(port), TTL_INIT)
            _index_dict[key] = rfc
    finally:
        sock.close()

    print("RFC file downloaded: " + str(num))
    diff = time.time() - start_time
    file_counter += 1
    sinT = open(sinT_name, "a")
    totT = open(totT_name, "a")

    sinT.write(str(num) + "," + str(diff) + "\n")

    total_time += diff

    totT.write(str(file_counter) + "," + str(total_time) + "\n")

    sinT.close()
    totT.close()

def search(num):
    return {v for k,v in _index_dict.items() if k.startswith(str(num))}

def look(num):
    global HOST, PORT
    found = False
    temp_index = search(num)
    if not temp_index:

        data = p_queri()
        for d in data:
            if(len(d) == 0):
                continue
            peer = d.split(":")
            hostname = peer[0]
            port = peer[1]
            if str(hostname) == str(HOST) and str(port) == str(PORT):
                continue
            rfc_queri(hostname, port)
            temp_index = search(num)
            
            if temp_index:
                first_temp_index = next(iter(temp_index))
                git_rfc(first_temp_index.get_hostname(), first_temp_index.get_port(), num)
                found = True
                break
        if not found:
            print("RFC not in P2P network: " + str(num) + "\n")
    else:
        first_temp_index = next(iter(temp_index))
        if HOST == first_temp_index.get_hostname() and PORT == first_temp_index.get_port():
            print("Already in this peer: " + str(num) + "\n\n")
        else:
            first_temp_index = next(iter(temp_index))
            git_rfc(first_temp_index.get_hostname(), first_temp_index.get_port(), num)

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
        rfc_query = re.search('RFCQuery: (.+) (\d+)', command)
        # Numbers are hostname, port number and RFC number
        get_rfc = re.search('GetRFC: (.+) (\d+) (\d+)', command) 
        find = re.search('Search: (\d+)$', command)
        find_many = re.search('Search: (\d+)-(\d+)', command)
        if register:
            regis()
        elif keep_alive:
            keep_aliveB()
        elif leave:
            leaveB()
        elif p_query:
            print(str(p_queri()))
        elif rfc_query:
            hostname = rfc_query.group(1)
            port = rfc_query.group(2)
            data = rfc_queri(hostname, port)
        elif get_rfc:
            hostname = get_rfc.group(1)
            port = get_rfc.group(2)
            num = get_rfc.group(3)
            git_rfc(hostname, port, num)
        elif find:
            num = find.group(1)
            look(num)
        elif find_many:
            start = find_many.group(1)
            end = find_many.group(2)
            indices = list(range(int(start), int(end) + 1))
            random.shuffle(indices)
            for x in indices:
                print("File:" + str(x))
                look(x)
        else:
            print("Invalid command.\n")

if __name__ == "__main__":

    e = threading.Event()
    try:
        # Sets values based on user input from command-line
        HOST, LOCATION, PORT = sys.argv[1], sys.argv[2], int(sys.argv[3])
        
        # Error check in case user didn't include / at end of location
        if(LOCATION[-1] != "/"):
            LOCATION += "/"

        header_text = "t1"
        folder_name = LOCATION[LOCATION[:-1].rfind("/") + 1:-1]

        # sinT_name = LOCATION + header_text + "_" + folder_name + "_st.csv"
        # totT_name = LOCATION + header_text + "_" + folder_name + "_tt.csv"

        sinT_name = header_text + "_" + folder_name + "_st.csv"
        totT_name = header_text + "_" + folder_name + "_tt.csv"

        sinT = open(sinT_name, "w+")
        totT = open(totT_name, "w+")

        sinT.close()
        totT.close()

        # Loops through all files to add them to the dictionary by RFC number
        for root, dirs, filenames in os.walk(LOCATION):
            for f in filenames:
                rfc_num = f[:-4] # removes .txt part of filename 
                rfc = RFCIndex(rfc_num, getTitle(LOCATION + f), HOST, PORT, TTL_INIT)
                _index_dict[str(rfc_num) + "_" + HOST + "_" + str(PORT)] = rfc

        server = ThreadedRFCServer((HOST, PORT), RFCServer)
        #print(server)

        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        e.set()
        # Thread for decrementing TTL for RFC indexes
        t1 = threading.Thread(target=ticker, args=(e, _index_dict))
        t1.start()
        # Thread for taking user input
        t2 = threading.Thread(target=user_input, args=(e,))
        t2.start()

    except(KeyboardInterrupt, SystemExit):
        print("Exiting...")

        e.clear()
        server.shutdown()
        sys.exit()

