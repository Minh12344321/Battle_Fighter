import socket
import threading

# Server configuration
HOST = '127.0.0.4'
PORT = 12345
clients = []  # List to store connected clients

def handle_client(client_socket, client_address, player_number):
    print(f"[New connection] {client_address} connected as Player {player_number}")
    client_socket.send(f"Welcome Player {player_number}".encode())

    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"[Player {player_number}] {message}")
            # Forward the player's position to the other client
            for client in clients:
                if client != client_socket:
                    client.send(message.encode())
        except:
            break

    # Remove the client and close the connection
    print(f"[Disconnected] Player {player_number} has disconnected.")
    clients.remove(client_socket)
    client_socket.close()

# Start server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(2)  # Allow only 2 clients to connect

    print(f"[Listening] Server is running at {HOST}:{PORT}")

    player_number = 1
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)

        # Assign player number and handle the client in a separate thread
        threading.Thread(target=handle_client, args=(client_socket, client_address, player_number)).start()
        player_number += 1

# Run server
if __name__ == "__main__":
    start_server()
