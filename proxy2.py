from asyncio import sleep
import socket
import struct
import hashlib
import os
import pickle
import time

proxy2_addr = "10.9.0.4"
proxy2_port = 30700
proxy1_port = 20700
end_user_port = 10545
MAX_RECV_BYTES = 65535
MAX_SENT_BYTES = 65000



class proxy2:

    def __init__(self):
        self.md5 = ""
        self.file_name = ""
        self.file_end = ""
        self.file_bytes = bytearray(0)

    def proxy2(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(("127.0.0.1", proxy2_port))
        print("Proxy2 is listening.")

        packet, address = udp_socket.recvfrom(MAX_RECV_BYTES)
        print("Packet received from proxy1 from ." + str(address))

        request_type = int.from_bytes(packet[0:4], byteorder="big")
        data_length = int.from_bytes(packet[40:44], byteorder='big')
        if request_type == 0:
            self.md5 = packet[4:36].decode("utf-8")
            self.accept_upload_request1(udp_socket, packet, address)
        else:
            print("ERROR: Wrong request type.")
            exit(-1)

        readable_hash = hashlib.md5(self.file_bytes).hexdigest()

        print("readable hash: " + readable_hash)
        print("received hash: " + self.md5)
        if self.md5 != readable_hash:
            print("FRAUD!!!!")
            exit(-1)

        udp_socket.close()

        packet = bytearray(0)
        packet += self.md5.encode("utf-8")
        packet += len(self.file_bytes).to_bytes(4, byteorder="big")
        packet += self.file_end.encode("utf-8")
        packet += self.file_bytes

        self.send_packet_via_tcp(packet)

    def accept_upload_request1(self, s: socket, packet, dest):
        s.setblocking(False)
        last_seq_num = 0

        request_type = int.from_bytes(packet[0:4], byteorder='big')
        self.md5 = packet[4:36].decode("utf-8")
        excepted_sequence_num = int.from_bytes(packet[36:40], byteorder='big')
        data_length = int.from_bytes(packet[40:44], byteorder='big')
        self.file_end = packet[44:47].decode("utf-8")

        self.file_bytes += packet[47:]
        self.send_ack(excepted_sequence_num, s, dest)

        while 1:
            current_time = time.time()
            while time.time() <= current_time + 3:
                try:
                    packet = None
                    packet, address = s.recvfrom(MAX_RECV_BYTES)
                except:
                    continue

                if packet is not None:
                    request_type = int.from_bytes(packet[0:4], byteorder='big')
                    excepted_sequence_num = int.from_bytes(packet[4:8], byteorder='big')
                    data_length = int.from_bytes(packet[8:12], byteorder='big')

                    if len(packet[12:]) < data_length:
                        continue

                    self.file_bytes += packet[12:]

                    if request_type != 0 and request_type != 27:
                        print("FRAUD!!!")
                        return
                    last_seq_num = excepted_sequence_num

                    if request_type == 27:
                        self.send_ack(excepted_sequence_num, s, dest, ack_type=17)
                        break
                    self.send_ack(excepted_sequence_num, s, dest)
            if request_type == 27: break
            self.send_ack(last_seq_num, s, dest)
        s.setblocking(True)
        print("finished an upload request")

    def send_ack(self, last_seq_num: int, s: socket, dest, ack_type=16):
        packet = struct.pack("2h", ack_type, last_seq_num)
        s.sendto(packet, dest)

    def send_packet_via_tcp(self, packet):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ADDR = ("127.0.0.1", end_user_port)
        """ Connecting to the server. """
        tcp_socket.connect(ADDR)

        counter = 0
        while counter + MAX_SENT_BYTES <= len(packet):
            tcp_socket.send(packet[counter:counter+MAX_SENT_BYTES])
            counter += MAX_SENT_BYTES
        tcp_socket.send(packet[counter:])
        tcp_socket.close()
        return


if __name__ == "__main__":
    proxy22 = proxy2()
    proxy22.proxy2()
