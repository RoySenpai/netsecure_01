import socket
import hashlib
import struct

sender_addr = "10.9.0.2"
proxy1_addr = "10.9.0.3"
MAX_SENT_BYTES = 65000


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

        packet = bytearray(0)
        packet += readable_hash.encode("utf-8")
        packet += len(file_bytes).to_bytes(4, byteorder="big")
        print("file bytes: ", len(file_bytes))
        packet += file_name[len(file_name)-3:len(file_name)].encode("utf-8")
        print(file_name[len(file_name)-3:len(file_name)])
        packet += file_bytes

        counter = 0
        while counter + MAX_SENT_BYTES <= len(packet):
            client.send(packet[counter:counter+MAX_SENT_BYTES])
            counter += MAX_SENT_BYTES
            print(len(packet[counter:]))
        client.send(packet[counter:])

        print(len(packet))


if __name__ == "__main__":
    sender1 = sender()
    sender1.sender()
