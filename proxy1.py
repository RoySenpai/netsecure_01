import socket
import struct
import hashlib

proxy1_port = 20700
proxy2_port = 30700
MAX_RECV_BYTES = 65535
MAX_SENT_BYTES = 65000
IP = socket.gethostbyname(socket.gethostname())

proxy1_addr = "10.9.0.3"
proxy2_addr = "10.9.0.4"
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
        readable_hash = packet[0:32].decode("utf-8")
        data_len = int.from_bytes(packet[32:36], byteorder='big')
        self.file_end = packet[36:39].decode("utf-8")
        self.file_bytes = packet[39:]
        counter = len(self.file_bytes)

        while counter < data_len:
            packet = client_socket.recv(MAX_SENT_BYTES)
            self.file_bytes += packet
            counter += len(packet)

        print("received file size: ", len(self.file_bytes[0:data_len]))
        self.md5 = hashlib.md5(self.file_bytes).hexdigest()
        print("received hash: ", self.md5)
        print("readable hash: " + readable_hash)
        if self.md5 != readable_hash:
            print("FRAUD!!!!")
            exit(-1)
        client_socket.close()
        server.close()

    def send_packet_via_rudp(self, proxy2_ip_addr):
        chunk_size = 16384
        recent_ack_packet_num = 0
        current_read, excepted_sequence_num, request_type = 0, 1, 0
        List = []
        file_size = len(self.file_bytes)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((proxy1_addr, proxy1_port))
        print("RUDP client is listening on port: ", proxy1_port)
        dest = (proxy2_ip_addr, proxy2_port)
        print("got connected to ", str(dest))

        packet = bytearray(0)
        packet += request_type.to_bytes(4, byteorder="big")
        packet += self.md5.encode("utf-8")
        packet += excepted_sequence_num.to_bytes(4, byteorder="big")
        packet += chunk_size.to_bytes(4, byteorder="big")
        packet += self.file_end.encode("utf-8")
        packet += self.file_bytes[0:chunk_size]

        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)

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
            packet += data_length.to_bytes(4, byteorder="big")
            packet += self.file_bytes[current_read:current_read + chunk_size]

            s.sendto(packet, dest)
            ack, address = s.recvfrom(MAX_RECV_BYTES)
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
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        if ack_type == 17:
            print("finished with: " + str(address[0]))
        s.close()
        return


if __name__ == "__main__":
    proxy11 = proxy1()
    proxy11.get_packet_via_tcp()
    proxy11.send_packet_via_rudp("10.9.0.4")