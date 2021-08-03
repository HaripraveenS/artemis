from socket import *

SERVER_PORT = 8079 
SERVER_IP = "127.0.0.1"

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

request = input("Enter request: ")

if len(request) == 0:
    request = "GET www.google.com HTTP/1.1"
client_socket.send(request.encode('utf-8'))
server_output = client_socket.recv(1024)

print("Main HTTP Message: ", server_output.decode().split("\r\n")[0])
print("Server Output: ", server_output)
client_socket.close()