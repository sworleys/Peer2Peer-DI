import socketserver

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
   
