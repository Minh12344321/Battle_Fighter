import socket
import threading

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received: {message}")
            broadcast(message, client_socket)
        except:
            break

def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            client.send(message.encode('utf-8'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5555))
server.listen(5)

clients = []

print("Server started...")
while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    print(f"Connection from {addr} established.")
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()
