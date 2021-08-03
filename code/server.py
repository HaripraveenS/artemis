import time
import os
import sys
from socket import *
import threading

SERVER_PORT = 8079
MAX_CLIENTS = 10
MAX_REQUEST_LEN = 1024
class Server:

    def __init__(self):
        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        except error as e:
            print("Failed to create server due to " ,e)
        # bind the socket to a public/local host, and a port
        self.server_socket.bind(('', SERVER_PORT))
        # allowing up to 10 client connections
        self.server_socket.listen(MAX_CLIENTS)
        message = "Host Name: Localhost and Host address: 127.0.0.1 and Host port: " + str(SERVER_PORT) + "\n"
        print("Server is ready to listen for clients...")

    def handle_requests(self):
        print("listening")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(client_address,client_socket)
            d = threading.Thread(name=str(client_address), target=self.proxy_thread, 
                    args=(client_socket, client_address))
            d.setDaemon(True)
            d.start()
        self.server_socket.close()

    def proxy_thread(self,client_socket,client_address):
        client_request = client_socket.recv(1024)
        parsed_address = self.parse_url(client_request)
        print("created thread...")
        # return "hello"
        message = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
        bmessage = message.encode('utf-8')
        client_socket.send(bmessage)

    def parse_url(self,address):
        print(address)
        address = address.decode()
        request_type = address.split(' ')

if __name__ == "__main__":
    server = Server()
    server.handle_requests()
