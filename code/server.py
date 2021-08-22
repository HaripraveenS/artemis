'''
TODO:
- Time (kitta time hua h) : Loay
- HTTPS (?) : Both
- Add post request : 
- Output Color : 
- IPs in blacklisting : 


CHANGELOG: 

15/08 LOAY
- Added authentication/admins
- Changed parsing code to allow auth

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
from typing import Callable
import re, string
import base64
import logging
import argparse
from datetime import datetime, date, time, timedelta

parser = argparse.ArgumentParser(description = "proxy server")
parser.add_argument("--server_port", default = 8079, type = int)
parser.add_argument("--cache_size", default = 5, type = int)
parser.add_argument("--max_clients", default = 10, type = int)
args = parser.parse_args()

# SERVER_PORT = 8079
# MAX_CLIENTS = 10
# CACHE_SIZE = 5
SERVER_PORT = args.server_port
MAX_CLIENTS = args.max_clients
CACHE_SIZE = args.cache_size
MAX_REQUEST_LEN = 1024
CACHE_PATH = "./cache/"
BLACKLIST_PATH = "./blacklist.txt"
ADMINS_PATH = "./admins.txt"
MIN_OCCURENCE = 2
'''
setup functions
'''

def init_cache():
    if not os.path.isdir(CACHE_PATH):
        os.mkdir(CACHE_PATH)
    else:
        for file in os.listdir(CACHE_PATH):
            os.remove(os.path.join(CACHE_PATH,file))




class Server:
    def __init__(self,logger):
        self.logger = logger
        self.filelog = {}
        self.current_cache = []
        # self.

        try:
            self.server_socket = socket(AF_INET, SOCK_STREAM)
            self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        except error as e:
            self.logger.error('Failed to create server due to %s' ,e)
        # bind the socket to a public/local host, and a port
        self.server_socket.bind(('', SERVER_PORT))
        # allowing up to 10 client connections
        self.server_socket.listen(MAX_CLIENTS)

        # CREATING BLACKLIST ARRAY
        with open(BLACKLIST_PATH) as f:
            self.blocked = f.read().splitlines()
        self.logger.info("Blacklist ready...")

        with open(ADMINS_PATH) as f:
            self.admins = []
            # print("ADMINS: ")
            for admin in f.read().splitlines():
                self.admins.append(str(base64.b64encode(admin.encode('utf-8'))))
                # print(admin[:admin.find(":")])
                # self.admins.append(admin)
        self.logger.info("Admins ready...")


        message = "Host Name: Localhost and Host address: 127.0.0.1 and Host port: " + str(SERVER_PORT) + "\n"
        message += "Max Cache Size: " + str(CACHE_SIZE) + " Max Clients: " + str(MAX_CLIENTS) + "\n"
        # print("Server is ready to listen for clients...")
        self.logger.info(message)
        self.logger.info("Server is ready to listen for clients...")
 
    
    def handle_requests(self):
        # print("Listening...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            # print("Client Address: ", client_address[0])
            # print("Client Port: ", client_address[1])
            client_details_log = "Client Details:- \n"
            client_details_log += "Client host name: "+str(client_address[0]) + "\nClient port number: "+str(client_address[1]) + "\n"
            client_socket_details = getaddrinfo(str(client_address[0]), client_address[1])
            client_details_log += "Socket family: "+str(client_socket_details[0][0]) + "\n"
            client_details_log += "Socket type: "+str(client_socket_details[0][1]) + "\n"
            client_details_log += "Socket protocol: "+str(client_socket_details[0][2]) + "\n"
            client_details_log += "Timeout: "+str(client_socket.gettimeout()) + "\n"
            # print(client_address,client_socket) # CONFUSING REDUNDANT USELESS INFORMATION UNCOMMENT IF DEBUGGING
            self.logger.info(client_details_log)
            d = threading.Thread(name=str(print), target=self.proxy_thread, 
                    args=(client_socket, client_address))
            d.setDaemon(True)
            d.start()

    def get_cache_size(self):
        return sum(os.path.getsize(f) for f in os.listdir(CACHE_PATH) if os.path.isfile(f))

    def to_cache_file(self, filepath):
        try:
            pattern = re.compile('[\W_]+')
            filepath_wo_slash = pattern.sub('_', filepath)
            # print("intocache")
            print(filepath_wo_slash)
            print(self.filelog[filepath_wo_slash])
            occurences = self.filelog[filepath_wo_slash]
            curr_time = datetime.now()
            if len(occurences) >= MIN_OCCURENCE:
                if occurences[len(occurences) - MIN_OCCURENCE + 1] + timedelta(days=1) \
                    > curr_time:
                    return True
                else :
                    print(occurences[len(occurences) - MIN_OCCURENCE + 1] + timedelta(days=1))
                    print(curr_time)
                    print(occurences[len(occurences) - MIN_OCCURENCE + 1] + timedelta(days=1) \
                    < curr_time)
            return False
        except KeyError as e:
            return False


    def cache_hit(self, filepath):
        # pass
        pattern = re.compile('[\W_]+')
        filepath_wo_slash = pattern.sub('_', filepath)
        cache_filepath = os.path.join(CACHE_PATH, filepath_wo_slash)
        # print("cache_filepath: ", cache_filepath)
        res = {}
        try :
            cached_file = open(cache_filepath, "r")
            response_message = ""
            cached_file.close()
            with open(cache_filepath) as f:
                for line in f:
                    response_message += line
            self.logger.info("CACHE HIT...")

            return {
                "hit": True,
                "file": response_message,
                "name":filepath_wo_slash
            }
        except IOError as e:
            self.logger.info("CACHE MISS...")
            return {
                "hit":False,
                "name":filepath_wo_slash
            }

    def proxy_thread(self,client_socket,client_address):
        self.logger.info("\nCREATED THREAD...\n")
        client_request = client_socket.recv(1024) # CLIENT REQUEST IS "GET www.google.com HTTP/1.1"
        parsed_address = self.parse_request(client_request)

        self.logger.info("\nPARSED ADDRESS:")
        self.logger.info(parsed_address)
        # self.logger.info("PARSED ADDRESS\n" + "#"* 50)

        # BLACKLIST CHECK
        if self.check_in_blacklist(parsed_address):
            client_socket.send(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            client_socket.close()
            return

        if parsed_address["type"] == "GET":
            '''
                Adding caching here
            '''
            cache_out = self.cache_hit(parsed_address["url"] + parsed_address["file"])
            if cache_out["hit"] == True:
                # print("cache hit")
                # print(cache_out["file"])
                currtime = datetime.now()
                self.filelog[cache_out["name"]].append(currtime)
                client_socket.send(cache_out["file"].encode('utf-8'))
                client_socket.close()
                return
                    # return cache_out["file"]
            try:
                proxy_socket = socket(AF_INET, SOCK_STREAM)
            except error as e:
                self.logger.error("Proxy socket could not be created because %s", e)


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
                        web_response = proxy_socket.recv(10000)
                    except timeout:
                        if len(web_response_append) <= 0:
                            timeout_flag = True
                        break
                    if len(web_response) > 0:
                        web_response_append += web_response
                    else:
                        break

                # APPEND SERVER DETAILS HERE

                if timeout_flag:
                    client_socket.send("HTTP/1.1 408 Request timeout\r\n\r\n")
                else:
                    # IF NO TIMEOUT, THEN SEND ACTUAL MESSAGE
                    client_socket.send(web_response_append)
                    currtime = datetime.now()
                    if cache_out["name"] in self.filelog.keys():
                        self.filelog[cache_out["name"]].append(currtime)
                        print(self.filelog[cache_out["name"]])
                    else : 
                        self.filelog[cache_out["name"]] = [currtime]
                        print(self.filelog[cache_out["name"]])

                    if self.to_cache_file(parsed_address["url"] + parsed_address["file"]):
                        self.logger.info("caching")
                        cache_newfile = parsed_address["url"] + parsed_address["file"]
                        pattern = re.compile('[\W_]+')
                        cache_newfile_wo_slash = pattern.sub('_', cache_newfile)
                        if len(self.current_cache) == CACHE_SIZE: 
                            self.delete_from_cache()
                        cache_newfile_path = os.path.join(CACHE_PATH,cache_newfile_wo_slash)
                        self.current_cache.append(cache_newfile_wo_slash)
                        proxy_new_file = open(cache_newfile_path, "wb")
                        # writing the entire response to file
                        proxy_new_file.write(web_response_append)
                        proxy_new_file.close()
                        proxy_socket.close()

            except error as e: 
                client_socket.send(b'HTTP/1.1 404 not found\r\n\r\n')
                self.logger.error("Could not access server, 404: %s", e)
            client_socket.close()

        else:
            # IF REQUEST ISN'T GET, STOP EVERYTHING CLOSE CONNECTION 
            self.logger.error("Request other than GET issued, stopping...")
            
            client_socket.send(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            client_socket.close()
        return

    def delete_from_cache(self):
        last_access = []
        for file in self.current_cache:
            last_access.append(self.filelog[file][-1])
        ind = last_access.index(min(last_access))
        del_file_path = os.path.join(CACHE_PATH, self.current_cache[ind])
        self.current_cache.pop(ind)
        os.remove(del_file_path)


    def parse_request(self,address):
        print(address)
        address = address.decode()
        parsed_address = {} 
        address = str(address)
        addr_lines = str(address).split('\n')

        # DOING PARSING OF THE FIRST LINE (GET www.xyz.com:8080/abc HTTP/1.1)
        split_address = addr_lines[0].split(' ')
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

        # DOING PARSING OF AUTHENTICATION HEADER (CAN ADD OTHER HEADERS AS WELL)
        parsed_address["auth"] = addr_lines[1].split(" ")[2]
        return parsed_address

    def check_in_blacklist(self, parsed_address):
        # URLS SAVED, NOT IP ADDRESSES
        # AUTHENTICATION HAPPENS HERE
        self.logger.info("Checking for blacklist")
        if parsed_address["url"] in self.blocked:
            self.logger.info("server is in blacklist")
            if(parsed_address["auth"] in self.admins):
                self.logger.info("ADMIN PRIVILEGES, ALLOWING BLACKLISTED REQUEST")
                return False
            else:
                self.logger.info("USER DOESN'T HAVE ACCESS, BLOCKING BLACKLISTED REQUEST")
                return True
        return False
        
from pathlib import Path


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s')
                        # filemode='w')
    logger=logging.getLogger("artemis")
    logger.setLevel(logging.DEBUG)
    init_cache()
    server = Server(logger)
    server.handle_requests()
