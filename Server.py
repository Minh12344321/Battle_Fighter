import socket
import threading

# Địa chỉ và cổng server
HOST = '127.0.0.1'  # Địa chỉ IP của máy chủ
PORT = 12345        # Cổng để lắng nghe kết nối

# Tạo socket cho server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)  # Lắng nghe tối đa 2 kết nối (2 người chơi)

print("Server started")

clients = []

# Hàm xử lý dữ liệu từ client
def handle_client(client_socket, player_id):
    while True:
        try:
            # Nhận dữ liệu từ client
            data = client_socket.recv(1024).decode()
            if not data:
                break
            print(f"Receive player{player_id}: {data}")
            
            # Gửi dữ liệu cho người chơi khác
            for client in clients:
                if client != client_socket:
                    client.sendall(f"{player_id}:{data}".encode())
        
        except Exception as e:
            print(f"Error to receive {player_id}: {e}")
            break

    client_socket.close()
    clients.remove(client_socket)
    print(f"Player {player_id} disconnected")

# Chấp nhận kết nối từ 2 người chơi
for player_id in range(2):
    client_socket, addr = server_socket.accept()
    print(f"Connect to {addr}")
    clients.append(client_socket)
    
    # Tạo một luồng xử lý riêng cho mỗi client
    threading.Thread(target=handle_client, args=(client_socket, player_id + 1)).start()
