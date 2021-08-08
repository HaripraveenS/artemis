'''
TODO:
- Add authentication for blacklisted URLs
- Add caching
- Add time (print when conenction closed)
- Add CIDR blacklisting (currently only blacklisting URL)
- Add caching once everything works perfectly
- Add support for POST request

CHANGELOG: 
08/08 LOAY
- Added parsing (removal http://, adding filepath, adding portnumber)
- Added calls to filepath (handling like google.com/abc/xyz, not just handling main url)
- Added blacklisting
'''

import time
import os
import sys
from socket import *
import threading
from pprint import *

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

        # CREATING BLACKLIST ARRAY
        with open("./blacklist.txt") as f:
            self.blocked = f.read().splitlines()
        print("BLACKLIST: ", self.blocked)
        print("Blacklist ready...")

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

        print("#"* 50 + "\nPARSED ADDRESS")
        pprint(parsed_address)
        print("PARSED ADDRESS\n" + "#"* 50)

        # BLACKLIST CHECK
        if self.check_in_blacklist(parsed_address):
            print("DESTINATION SERVER IS BLACKLISTED")
            client_socket.send(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            client_socket.close()
            return

        
        if parsed_address["type"] == "GET":
            try:
                proxy_socket = socket(AF_INET, SOCK_STREAM)
            except error as e:
                print(f"Proxy socket could not be created because {e}")

            try:
                proxy_socket.settimeout(2)
                proxy_socket.connect((parsed_address["url"], parsed_address["port"])) # PROXY PORT IS GENERALLY 8

                if parsed_address["file"]:
                    web_request = bytes("GET /" + parsed_address["file"][1:] + " HTTP/1.1\nHost: " + parsed_address["url"] + "\n\n", 'utf-8') # SKIP FIRST LINE, CONSIDER ALL ELSE
                else:
                    web_request = bytes("GET / HTTP/1.1\nHost: "  + parsed_address["url"] + "\n\n", 'utf-8') # WTF DOES THIS DO 


                proxy_socket.send(web_request)

                # GET https://www.google.com.sa/imghp?hl=en&authuser=0&ogbl HTTP/1.1
                # GET http://www.google.com/abc/xyz HTTP/1.1

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
            except error as e: 
                client_socket.send(b'HTTP/1.1 404 not found\r\n\r\n')
                print(f"Could not access server, 404: {e}")
            client_socket.close()

        else:
            # IF REQUEST ISN'T GET, STOP EVERYTHING CLOSE CONNECTION 
            print("Request other than GET issued, stopping.")
            client_socket.send(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            client_socket.close()
        return


    def parse_request(self,address):
        # BAREBONES AT THE MOMENT, CAN COPY PASTE CODE FROM ELSEWHERE (NO BRAIN NEEDED)
        print(address)
        address = address.decode()
        parsed_address = {} 

        split_address = address.split(' ')
        parsed_address["type"] = split_address[0] # WILL USUALLY BE GET

        # WE NEED TO REMOVE THE HTTP:// PART TO GET TO THE URL
        fullurl = split_address[1] # CONTAINS EVERYTHING LIKE https://www.google.com/abc/xyz

        # REMOVING https://
        if "//" in fullurl:
            nohttp_url = fullurl.split("//")[1]
        else:
            nohttp_url = fullurl

        # REMOVING TRAILING / LIKE google.com/ OR FINDING FILE PATH
        if "/" in nohttp_url:
            main_url = nohttp_url.split("/")[0]
            filepath_list = nohttp_url.split("/")[1:] # THIS RETURNS A LIST LIKE ['abc', 'xyz'] 
            filepath_str = ""
            for path in filepath_list:
                filepath_str += "/" + path

        else:
            main_url = nohttp_url
            filepath_str = ""

        parsed_address["url"] = main_url # URL OF REQUEST
        parsed_address["file"] = filepath_str # FILEPATH

        # ADDING PORT NUMBERS
        if ":" in nohttp_url:
            parsed_address["port"] = int(main_url.split(':')[1])
        else: 
            parsed_address["port"] = 80 

        return parsed_address

    def check_in_blacklist(self, parsed_address):
        # URLS SAVED, NOT IP ADDRESSES
        if parsed_address["url"] in self.blocked:
            return True
        return False
        
        

if __name__ == "__main__":
    server = Server()
    server.handle_requests()
