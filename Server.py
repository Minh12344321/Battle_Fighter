import socket
import threading

# Danh sách các kết nối từ client
clients = []

def handle_client(client_socket, player_id):
    global player1_pos, player2_pos
    try:
        while True:
            message = client_socket.recv(1024).decode()  # Nhận thông tin từ client
            
            if message:
                # Chia thông tin ra thành player_id và vị trí
                player_id, position = message.split(":")
                x, y = map(int, position.split(","))
                
                # Cập nhật vị trí của nhân vật theo player_id
                if player_id == "1":
                    player1_pos = [x, y]
                elif player_id == "2":
                    player2_pos = [x, y]
                
                # Thực hiện các hành động tiếp theo như vẽ lại màn hình, tính toán va chạm, v.v.
                print(f"Player {player_id} updated position to ({x}, {y})")
    except:
        print("Client disconnected")
        clients.remove(client_socket)
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))  # Địa chỉ server
    server_socket.listen(2)  # Chỉ chấp nhận 2 client

    print("Server started and waiting for connections...")
    
    while len(clients) < 2:  # Chờ cho đến khi 2 client kết nối
        client_socket, addr = server_socket.accept()
        print(f"New connection: {addr}")
        clients.append(client_socket)

        # Xác định player_id (Player 1 hoặc Player 2)
        player_id = len(clients)
        threading.Thread(target=handle_client, args=(client_socket, player_id)).start()

start_server()
