import socket
import struct
import hashlib 

end_user_addr = "10.9.0.5"
MAX_RECV_BYTES = 65535
end_user_port = 10545

class enduser:
    def enduser(self):
        print("[STARTING] Server is starting.")
        """ Staring a TCP socket. """
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = ('', end_user_port)

        """ Bind the IP and PORT to the server. """

        tcp_socket.bind(ADDR)

        """ Server is listening, i.e., server is now waiting for the client to connected. """
        tcp_socket.listen()
        print("[LISTENING] Server is listening.")

        """ Server has accepted the connection from the client. """
        client_socket, client_address = tcp_socket.accept()
        print(f"[NEW CONNECTION] {client_address} connected.")
        print()

        packet = client_socket.recv(MAX_RECV_BYTES)
        readable_hash = packet[0:32].decode("utf-8")
        file_size = int.from_bytes(packet[32:36], byteorder='big')
        file_end = packet[36:39].decode("utf-8")
        file_bytes = packet[39:]
        counter = len(packet[39:])

        while counter < file_size:
            packet = client_socket.recv(MAX_RECV_BYTES)
            file_bytes += packet
            counter += len(packet)

        if len(file_bytes) != file_size:
            print("FRAUD!!!!")
            exit(-1)

        hash1 = hashlib.md5(file_bytes).hexdigest()
        print("readable hash: " + readable_hash)
        print("received hash: " + hash1)
        if readable_hash != hash1:
            print("FRAUD!!!!")
            exit(-1)

        client_socket.close()
        tcp_socket.close()

        file = ""
        try:
            file = open(str(readable_hash) + "." + file_end, "wb+")
        except:
            raise

        file.write(file_bytes)
        file.close()
        client_socket.close()
        tcp_socket.close()


if __name__ == "__main__":
    enduser1 = enduser()
    enduser1.enduser()

