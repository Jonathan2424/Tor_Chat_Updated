import socket
import pickle

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto("GetServerList", ("127.0.0.1", 2000))
data, addr = client_socket.recvfrom(1024)
print pickle.loads(data)
