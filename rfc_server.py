import socketserver, re, socket, time, datetime, threading, sys
import linked_list

class RFC_Index(linked_list.Node):
    """
    """

    def __init__(self, num, title, hostname, ttl):
        self._num = num
        self._title = title
        self._hostname = hostname
        self._ttl = ttl

    def get_num(self):
        return self._num

    def get_title(self):
        return self._title

    def get_hostname(self):
        return self._hostname

    def get_ttl(self):
        return self._ttl

class RFCServer(socketserver.BaseRequestHandler):
    """
    """

    def handle(self):
        global _peer_list
        global _cookie_index
        self.data = str(self.request.recv(1024).strip(), "utf-8")

        rfc_query = re.search('RFCQuery: (\d+)', self.data)
        get_rfc = re.search('GetRFC: (\d+)', self.data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # A peer requests the RFC index from a remote peer.
        if rfc_query:
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            port = rfc_query.group(1)
            
            try:
                sock.connect((hostname, port))
                # Need to change data to head of LinkedList.toString()
                sock.sendall(bytes(data + "\n", "utf-8"))

                recieved = str(sock.recv(1024), "utf-8")

            finally:
                sock.close()

        # A peer requests to download a specific RFC document from a remote peer.
        elif get_rfc:
            try:
                hostname = socket.gethostbyaddr(self.client_address[0])[0]
            except:
                hostname = self.client_address[0]
            port = get_rfc.group(1)

            try:
                sock.connect((hostname, port))
                # Need to change data to RFC files.
                sock.sendall(bytes(data + "\n", "utf-8"))

                recieved = str(sock.recv(1024), "utf-8")

            finally:
                sock.close()
