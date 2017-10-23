import socket
import sys

# Sets host and port variables
HOST, PORT = "localhost", 65423

data = " ".join(sys.argv[1:])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
        sock.connect((HOST, PORT))
        sock.sendall(bytes(data + "\n", "utf-8"))

        recieved = str(sock.recv(1024), "utf-8")

finally:
    sock.close()

print("Sent:        {}".format(data))
print(recieved)


