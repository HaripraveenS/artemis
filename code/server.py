'''
TODO:

LOAY 03/07/2021:
- Make parsing robust (add http:// removal)
- Add url file indexing (currently only access hosts)
- Add port number parsing
- Add time (print when conenction closed)
- Add caching once everything works perfectly
- Add support for POST request
'''

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
        print("Listening...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print("Client Address: ", client_address[0])
            print("Client Port: ", client_address[1])
            # print(client_address,client_socket) # CONFUSING REDUNDANT USELESS INFORMATION UNCOMMENT IF DEBUGGING
            d = threading.Thread(name=str(print), target=self.proxy_thread, 
                    args=(client_socket, client_address))
            d.setDaemon(True)
            d.start()
        self.server_socket.close()

    def proxy_thread(self,client_socket,client_address):
        print("#"*20 + "\nCREATED THREAD...\n" + "#"*20)
        client_request = client_socket.recv(1024) # CLIENT REQUEST IS "GET www.google.com HTTP/1.1"
        parsed_address = self.parse_request(client_request)

        # BYTES VS STRING KI BAKCHODI HOGI
        # print("asdfasdf " * 50)
        # print(b"GET / HTTP/1.1\nHost: " + bytes(parsed_address["url"], 'utf-8') + b"\n\n")
        
        if parsed_address["type"] == "GET":
            try:
                proxy_socket = socket(AF_INET, SOCK_STREAM)
            except error as e:
                print(f"Proxy socket could not be created because {e}")

            try:
                proxy_socket.settimeout(2)
                proxy_socket.connect((parsed_address["url"], parsed_address["port"])) # PROXY PORT IS GENERALLY 8
            except error as e: 
                client_socket.send('HTTP/1.1 404 not found\r\n\r\n')
                print(f"Could not access server, 404: {e}")

            
            # BELOW LINE WAS TROUBLESOME
            web_request = b"GET / HTTP/1.1\nHost: "  + bytes(parsed_address["url"], 'utf-8') + b"\n\n" # WTF DOES THIS DO 

            proxy_socket.send(web_request)

            timeout_flag = False
            web_response_append = b""
            while True:
                try:
                    web_response = proxy_socket.recv(4096)
                except timeout:
                    if len(web_response_append) <= 0:
                        # KUCH BHI NAHI AAYA, SHURU SE HI TIMEOUT
                        timeout_flag = True
                    break
                if len(web_response) > 0:
                    web_response_append += web_response
                else:
                    # SAB KUCH AAGAYA, BREAK LOOP
                    break

            # APPEND SERVER DETAILS HERE

            if timeout_flag:
                # SHURU SE HI TIMEOUT
                client_socket.send("HTTP/1.1 408 Request timeout\r\n\r\n")
            else:
                # IF NO TIMEOUT, THEN SEND ACTUAL MESSAGE
                client_socket.send(web_response_append)
            proxy_socket.close()

        else:
            # IF REQUEST ISN'T GET, STOP EVERYTHING CLOSE CONNECTION 
            print("Request other than GET issued, stopping.")
            client_socket.send("HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            client_socket.close()


    def parse_request(self,address):
        # BAREBONES AT THE MOMENT, CAN COPY PASTE CODE FROM ELSEWHERE (NO BRAIN NEEDED)
        print(address)
        address = address.decode()
        parsed_address = {} 

        split_address = address.split(' ')
        parsed_address["type"] = split_address[0] # WILL USUALLY BE GET
        parsed_address["url"] = split_address[1] # URL OF REQUEST

        #CHANGE BELOW LINE
        parsed_address["port"] = 80 
        #CHANGE ABOVE LINE

        return parsed_address

if __name__ == "__main__":
    server = Server()
    server.handle_requests()
