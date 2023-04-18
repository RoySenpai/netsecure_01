import socket
import struct
import hashlib
import os
import random
import string
import time

proxy1_port = 20700
proxy2_port = 30700
MAX_RECV_BYTES = 65535
MAX_SENT_BYTES = 65000
IP = socket.gethostbyname(socket.gethostname())

proxy1_addr = "10.9.0.3"
TCP_PORT = 20989


class proxy1:
    def __init__(self):
        self.md5 = ""
        self.file_name = ""
        self.file_end = ""
        self.file_bytes = ""

    def get_packet_via_tcp(self):
        print("[STARTING] Server is starting.")
        """ Staring a TCP socket. """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = ('', TCP_PORT)
        """ Bind the IP and PORT to the server. """
        server.bind(ADDR)
        """ Server is listening, i.e., server is now waiting for the client to connected. """
        server.listen()
        print("[LISTENING] Server is listening.")
        """ Server has accepted the connection from the client. """
        client_socket, client_address = server.accept()
        print(f"[NEW CONNECTION] {client_address} connected.")
        print()

        packet = client_socket.recv(MAX_RECV_BYTES)
        print(len(packet))
        readable_hash = packet[0:32].decode("utf-8")
        data_len = int.from_bytes(packet[32:36], byteorder='big')
        print("data len: ", data_len)
        self.file_end = packet[36:39].decode("utf-8")
        print(self.file_end)
        self.file_bytes = packet[39:]
        counter = len(self.file_bytes)
        print("counter: ", counter)

        while counter < data_len:
            print("a")
            packet = client_socket.recv(MAX_SENT_BYTES)
            print(len(packet))
            self.file_bytes += packet
            counter += len(packet)
            print("counter: ", counter)

        print("file byter: ", len(self.file_bytes[0:data_len]))
        self.md5 = hashlib.md5(self.file_bytes).hexdigest()
        print(type(self.md5))
        print(self.md5)
        print("readable hash: " + readable_hash)
        if self.md5 != readable_hash:
            print("FRAUD!!!!")
            exit(-1)
        client_socket.close()
        server.close()

    def send_packet_via_rudp1(self, proxy2_ip_addr):
        chunk_size = 16384
        recent_ack_packet_num = 0
        current_read, excepted_sequence_num, request_type = 0, 1, 0
        List = []
        file_size = len(self.file_bytes)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", proxy1_port))
        print("RUDP client is listening on port: ", proxy1_port)
        dest = ("127.0.0.1", proxy2_port)
        print("got connected to ", str(dest))

        packet = bytearray(0)
        packet += request_type.to_bytes(4, byteorder="big")
        packet += self.md5.encode("utf-8")
        packet += excepted_sequence_num.to_bytes(4, byteorder="big")
        packet += chunk_size.to_bytes(4, byteorder="big")
        packet += self.file_end.encode("utf-8")
        print(self.file_end)
        packet += self.file_bytes[0:chunk_size]
        print("actual sent bytes: ", len(packet[44:]))

        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        print("expected sequence number: ", excepted_sequence_num)

        if ack_type != 16:
            print("FRAUD!!!!")
            return
        recent_ack_packet_num = excepted_sequence_num

        while current_read + chunk_size <= file_size:
            excepted_sequence_num += 1
            current_read += chunk_size
            List.append((excepted_sequence_num, current_read, current_read + chunk_size))
            request_type = 0
            data_length = chunk_size

            packet = bytearray(0)
            packet += request_type.to_bytes(4, byteorder="big")
            packet += excepted_sequence_num.to_bytes(4, byteorder="big")
            print("data length: ", data_length)
            packet += data_length.to_bytes(4, byteorder="big")
            print("data length: ", int.from_bytes(packet[8:12], byteorder="big"))
            print("current read + chunk: ", current_read, " ", chunk_size + current_read)
            packet += self.file_bytes[current_read:current_read + chunk_size]
            print("actual sent bytes: ", len(packet[12:]))

            s.sendto(packet, dest)
            print("sent packet ", excepted_sequence_num, " to ", dest)
            ack, address = s.recvfrom(MAX_RECV_BYTES)
            print("received ack from ", address)
            ack_type, excepted_sequence_num = struct.unpack("2h", ack)
            if ack_type != 16:
                print("FRAUD!!!!")
                return
            if excepted_sequence_num == recent_ack_packet_num:
                for i in List:
                    if i[0] > recent_ack_packet_num:
                        List.remove(i)
                current_read = List[len(List) - 1][2]
                excepted_sequence_num = recent_ack_packet_num
                print("current expected sequence number: ", excepted_sequence_num)
            else:
                recent_ack_packet_num = excepted_sequence_num
        # excepted_sequence_num += 1
        request_type = 27
        data_length = file_size - current_read

        packet = bytearray(0)
        packet += request_type.to_bytes(4, byteorder="big")
        packet += excepted_sequence_num.to_bytes(4, byteorder="big")
        packet += data_length.to_bytes(4, byteorder="big")
        packet += self.file_bytes[current_read: file_size]

        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        print("received ack from ", address)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        if ack_type == 17:
            print("finished with: " + str(address[0]))
        s.close()
        return

    def send_packet_via_rudp(self, proxy2_ip_addr):
        defult_chunk_size, chunk_size = 2048, 2048
        dup_ack_counter, recent_ack_packet_num = 0, 0
        current_read, excepted_sequence_num, request_type, flag = 0, 1, 0, 0
        List = []
        file_size = len(self.file_bytes)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", proxy1_port))
        print("RUDP client is listening on port: ", proxy1_port)
        dest = ("127.0.0.1", proxy2_port)
        print("got connected to ", str(dest))

        packet = bytearray(44 + 2048)
        packet[0:4] = request_type.to_bytes(4, byteorder="big")
        packet[4:36] = self.md5.encode("utf-8")
        packet[36:40] = excepted_sequence_num.to_bytes(4, byteorder="big")
        packet[40:44] = chunk_size.to_bytes(4, byteorder="big")
        packet[44:] = self.file_bytes[0:chunk_size]
        print("actual sent bytes: ", len(packet[44:]))

        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        print("expected sequence number: ", excepted_sequence_num)
        if ack_type != 16:
            print("FRAUD!!!!")
            return
        recent_ack_packet_num = excepted_sequence_num

        while current_read + chunk_size <= file_size:
            excepted_sequence_num += 1
            List.append((excepted_sequence_num, current_read, current_read + chunk_size))
            request_type = 0
            data_length = chunk_size

            packet = bytearray(12 + chunk_size)
            packet[0:4] = request_type.to_bytes(4, byteorder="big")
            packet[4:8] = excepted_sequence_num.to_bytes(4, byteorder="big")
            print("data length: ", data_length)
            packet[8:12] = data_length.to_bytes(4, byteorder="big")
            print("data length: ", int.from_bytes(packet[8:12], byteorder="big"))
            print("current read + chunk: ", current_read, " ", chunk_size + current_read)
            packet[12:] = self.file_bytes[current_read:current_read + chunk_size]
            print("actual sent bytes: ", len(packet[12:]))

            current_read += chunk_size

            s.sendto(packet, dest)
            print("sent packet ", excepted_sequence_num, " to ", dest)
            ack, address = s.recvfrom(MAX_RECV_BYTES)
            print("received ack from ", address)
            ack_type, excepted_sequence_num = struct.unpack("2h", ack)
            if ack_type != 16:
                print("FRAUD!!!!")
                return
            if excepted_sequence_num == recent_ack_packet_num:
                dup_ack_counter += 1
                if dup_ack_counter == 2:
                    if chunk_size < MAX_SEND_BYTES: chunk_size = int(chunk_size * 1.2)
                if dup_ack_counter > 2:
                    print("startover")
                    chunk_size = defult_chunk_size
                for i in List:
                    if i[0] > recent_ack_packet_num:
                        List.remove(i)
                current_read = List[len(List) - 1][2]
                excepted_sequence_num = recent_ack_packet_num
                print("current expected sequence number: ", excepted_sequence_num)
            else:
                recent_ack_packet_num = excepted_sequence_num
                dup_ack_counter = 0
                if chunk_size < MAX_SEND_BYTES: chunk_size *= 2
        excepted_sequence_num += 1
        request_type = 27
        data_length = file_size - current_read

        packet = bytearray(12 + file_size - current_read)
        packet[0:4] = request_type.to_bytes(4, byteorder="big")
        packet[4:8] = excepted_sequence_num.to_bytes(4, byteorder="big")
        packet[8:12] = data_length.to_bytes(4, byteorder="big")
        packet[12:] = self.file_bytes[current_read: file_size]

        request_type = int.from_bytes(packet[0:4], byteorder='big')
        print("request type: " + str(request_type))
        excepted_sequence_num = int.from_bytes(packet[4:8], byteorder='big')
        print("Excepted sequence number received1: " + str(excepted_sequence_num))
        data_length = int.from_bytes(packet[8:12], byteorder='big')
        print("data length: " + str(data_length))
        file_data = packet[12:]
        print("file data len: " + str(len(file_data)))

        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        print("received ack from ", address)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        if ack_type == 17:
            print("finished with: " + str(address[0]))
        s.close()
        return



if __name__ == "__main__":
    proxy11 = proxy1()
    proxy11.get_packet_via_tcp()
    proxy11.send_packet_via_rudp1("127.0.0.1")
