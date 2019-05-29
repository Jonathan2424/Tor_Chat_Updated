import socket
import select

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8820))

server_socket.listen(5)
open_client_sockets = []
messages_to_send = []
open_clients_data = {}

class ClientData:
    def __init__(self, sock):
        self.sock = sock
        self.name = None

    def setName(self, name):
        self.name = name

def send_waiting_messages(wlist):
    # sends waiting messages that need to be sent, only if the clients socket is writeable
    for message in messages_to_send:
        (client_socket, data) = message
        if client_socket in wlist:
            client_socket.send(data)
            messages_to_send.remove(message)

while True:
    num_of_clients = len(open_client_sockets)
    rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            open_client_sockets.append(new_socket)
            open_clients_data[new_socket] = ClientData(new_socket)
        else:
            data = current_socket.recv(1024)

            splitted_data = data.split(":")
            if splitted_data[0] == "ClientName":
                client_data = open_clients_data[current_socket]
                client_data.name = splitted_data[1]
            elif splitted_data[0] == "Quit":
                open_client_sockets.remove(current_socket)
                print "Connection with " + open_clients_data[current_socket].name + " closed"
            else:
                formated_data = "{0} - {1}".format(open_clients_data[current_socket].name,data)
                for s in open_client_sockets:
                    if s in wlist and s != current_socket:
                        s.send(formated_data)

