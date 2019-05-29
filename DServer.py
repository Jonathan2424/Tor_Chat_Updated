import socket
import select
import netifaces
import time
import pickle
import random


class TorServerInstanceTrack:
    def __init__(self, address, key):
        self.address = address
        self.update_time = time.time()
        self.key = key
        self.__THRESHOLD = 300

    def is_active(self):
        if time.time() - self.update_time > self.__THRESHOLD:
            return False

        return True

    def reset_time(self):
        self.update_time = time.time()

    def serialize(self):
        return "address={0}:key={1}".format(self.address, self.key)


class DServer:
    def __init__(self, port, ip, key):
        self.directory_addresses = {}
        self.port = port
        self.socket = None
        self.ip = ip
        self.key = key

    def main_loop(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(("0.0.0.0", self.port))

        self.directory_addresses[self.socket] = TorServerInstanceTrack(self.ip, self.key)

        last_time = time.time()
        while True:
            # if broadcast time elapsed... send broadcast notification:
            current_time = time.time()
            if current_time-last_time > 1:
                last_time = current_time
                self.socket.sendto("Tor server:{0}".format(self.key), (get_broadcast_address(self.ip), self.port))
            # check for arrival directory servers:
            rlist, wlist, xlist = select.select([self.socket], [self.socket], [])
            for current_socket in rlist:
                (data, address) = current_socket.recvfrom(1024)
                splitted_data = data.split(":")
                if splitted_data[0] == "Tor server":
                    print address
                    self.accumulate(address, current_socket, splitted_data[1])

                elif splitted_data[0] == "GetServerList":
                    self.directory_cleanup()
                    server_list_message = pickle.dumps(self.serialize_server_list())
                    print server_list_message
                    current_socket.sendto(server_list_message, address)

    def serialize_server_list(self):
        list = []
        for tor_socket in self.directory_addresses:
            obj = self.directory_addresses[tor_socket]
            print obj
            list.append(obj.serialize())
        return list

    def directory_cleanup(self):
        print self.directory_addresses
        for tor_socket in self.directory_addresses:
            obj = self.directory_addresses[tor_socket]
            if obj.is_active():
                return
            else:
                del self.directory_addresses

    def accumulate(self, tor_address, tor_socket, tor_key):
        if tor_socket in self.directory_addresses:
            obj = self.directory_addresses[tor_socket]
            if obj.is_active():
                print ("alive")
                obj.reset_time()
                return
            else:
                del self.directory_addresses

        self.directory_addresses[tor_socket] = TorServerInstanceTrack(tor_address, tor_key)

# accept directory address request from proxy


def get_broadcast_address(ip):
    for i in netifaces.interfaces():
            try:
                if netifaces.AF_INET in netifaces.ifaddresses(i):
                    if netifaces.ifaddresses(i)[netifaces.AF_INET][0]['addr'] == ip:
                        netmask = netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask']
                        print("Mask: ", netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask'])
            except:
                print "error"
                pass
    splitted_ip = ip.split('.')
    ip_number = 0
    for i in splitted_ip:
        print i
        ip_number *= 256
        ip_number += int(i)
    print "-----"
    splitted_netmask = netmask.split('.')
    print "splitted_netmask = {0}".format(splitted_netmask)
    netmask_number = 0
    full_netmask = 0
    for i in splitted_netmask:
        netmask_number *= 256
        full_netmask *= 256
        netmask_number += int(i)
        full_netmask += 255

    print ip_number, netmask_number, full_netmask

    subnet_common_IP = ip_number & netmask_number
    print subnet_common_IP
    subnet_ip_capacity = full_netmask ^ netmask_number
    print subnet_ip_capacity
    broadcast_number = subnet_common_IP + subnet_ip_capacity

    splitted_broadcast_number= []
    for i in xrange(0,4):
        remainder= broadcast_number%256
        print remainder
        broadcast_number /= 256
        if len(splitted_broadcast_number) == 0:
            splitted_broadcast_number.append(remainder)
        else:
            splitted_broadcast_number.insert(0, remainder)

    splitted_broadcast_number= '.'.join(str(i) for i in splitted_broadcast_number)
    print splitted_broadcast_number
    return splitted_broadcast_number


def main():
    my_dserver = DServer(2000, '10.51.101.99', random.randint(1000, 9999))
    my_dserver.main_loop()
    print "yehu"


if __name__ == '__main__':
    main()
