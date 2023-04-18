import socket
import hashlib
import struct

sender_addr = "10.9.0.2"
proxy1_addr = "10.9.0.3"


class sender:
    def sender(self):
        file_name = input("Enter the file name you want to send: ")

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ADDR = ("127.0.0.1", 20989)

        """ Connecting to the server. """
        client.connect(ADDR)
        print("Connected to the server.")

        with open(file_name, "rb") as f:
            file_bytes = f.read()  # read file as bytes
            readable_hash = hashlib.md5(file_bytes).hexdigest()
            print(type(readable_hash))
            print(readable_hash)
        packet = bytearray(32 + len(file_bytes))
        packet[0:32] = readable_hash.encode("utf-8")
        packet[32:35] = file_name[len(file_name)-3:len(file_name)].encode("utf-8")
        print(file_name[len(file_name)-3:len(file_name)])
        packet[35:] = file_bytes

        print(len(packet))
        client.send(packet)


if __name__ == "__main__":
    sender1 = sender()
    sender1.sender()
