from socket import *
import base64

SERVER_PORT = 8079 
SERVER_IP = "127.0.0.1"

client_socket1 = socket(AF_INET, SOCK_STREAM)
client_socket1.connect((SERVER_IP, SERVER_PORT))
client_socket2 = socket(AF_INET, SOCK_STREAM)
client_socket2.connect((SERVER_IP, SERVER_PORT))
client_socket3 = socket(AF_INET, SOCK_STREAM)
client_socket3.connect((SERVER_IP, SERVER_PORT))
client_socket4 = socket(AF_INET, SOCK_STREAM)
client_socket4.connect((SERVER_IP, SERVER_PORT))

request1 = "GET www.google.com/ HTTP/1.1 \nAuthorization: Basic "
request2 = "GET www.google.com/abc/xyz HTTP/1.1 \nAuthorization: Basic "
request3 = "GET https://jsonplaceholder.typicode.com/posts/1 HTTP/1.1 \nAuthorization: Basic " #BLACLISTED
request4 = "GET https://jsonplaceholder.typicode.com/posts/1 HTTP/1.1"
request4 += "\nAuthorization: Basic " + str(base64.b64encode("loay:1234".encode('utf=8')))
# if len(request) !=0 and len(authorization) != 0:
#     request += "\n Authorization: Basic " + base64.b64encode(authorization.encode('utf=8'))

# request += "\nAuthorization: Basic " + str(base64.b64encode(authorization.encode('utf=8')))

print("request1: ", request1)
print("request2: ", request2)
print("request3: ", request3)
print("request4: ", request4)
print("Sending Above Request to Server...\n")
client_socket1.send(request1.encode('utf-8'))
client_socket2.send(request2.encode('utf-8'))
client_socket3.send(request3.encode('utf-8'))
client_socket4.send(request4.encode('utf-8'))
print("SEND ALL REUESTS")
server_output1 = client_socket1.recv(1024)
server_output2 = client_socket2.recv(1024)
server_output3 = client_socket3.recv(1024)
server_output4 = client_socket4.recv(1024)
print("ALL RECEIVED")
print("Main HTTP Message1: ", server_output1.decode().split("\n")[0])
print("Main HTTP Message2: ", server_output2.decode().split("\n")[0])
print("Main HTTP Message3: ", server_output3.decode().split("\n")[0])
print("Main HTTP Message4: ", server_output4.decode().split("\n")[0])
# print("Server Output: ", server_output)
client_socket1.close()
client_socket2.close()
client_socket3.close()
client_socket4.close()