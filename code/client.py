'''

CHANGELOG

15/08 LOAY
- Added authentication
- Now sending multiline input with Authentication header (empty if not admin)
'''

from socket import *
import base64

SERVER_PORT = 8079 
SERVER_IP = "127.0.0.1"

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

request = input("Enter request: ")
authorization = input("Enter user:pass : ")

if len(request) == 0:
    # request = "GET www.google.com HTTP/1.1"
    request = "GET https://jsonplaceholder.typicode.com/ HTTP/1.1"
    request = "GET https://jsonplaceholder.typicode.com/ HTTP/1.1"
    request = "GET http://jsonplaceholder.typicode.com/posts/ HTTP/1.1"

# if len(request) !=0 and len(authorization) != 0:
#     request += "\n Authorization: Basic " + base64.b64encode(authorization.encode('utf=8'))

request += "\nAuthorization: Basic " + str(base64.b64encode(authorization.encode('utf=8')))

print("request: ", request)
print("Sending Above Request to Server...\n")
client_socket.send(request.encode('utf-8'))
server_output = client_socket.recv(1024)

print("Main HTTP Message: ", server_output.decode().split("\n")[0])
print("Server Output: ", server_output)
client_socket.close()