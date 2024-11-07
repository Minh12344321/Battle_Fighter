import pygame
import sys
import time
import socket
import os
import threading,inspect,json

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
assets_path1 = os.path.join(currentdir, 'Assets', 'Images')
assets_path2 = os.path.join(currentdir, 'Assets', 'Sound')
# Khởi tạo Pygame
pygame.init()

# Kích thước cửa sổ
WIDTH, HEIGHT = 1600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Đánh Nhau")
font = pygame.font.Font(None, 32)

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

BULLET_COLOR = (255, 255, 0)
PLAYER1_COLOR = (255, 255, 0)  # Màu sắc nhân vật 1
PLAYER2_COLOR = (255, 100, 100)  # Màu sắc nhân vật 2
AVATAR1_COLOR = (255, 255, 0)  # Màu sắc avatar cho player 1 (vàng)
AVATAR2_COLOR = GREEN    # Màu sắc avatar cho player 2 (xanh lá)
BUTTON_COLOR = BLACK
bg_color = WHITE

HOST = '127.0.0.4'  # Địa chỉ IP máy chủ
PORT = 12345        # Cổng kết nối

# Tạo hàm kết nối socket
def connect_to_server(ip, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, int(port)))
        return client_socket
    except Exception as e:
        print("Error:", e)
        return None  # Kết nối thất bại
    
client_socket = connect_to_server(HOST, PORT)

# Hàm nhận và xử lý thông điệp từ server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print("Nhận được từ server:", message)  # In thông điệp nhận được
        except:
            print("Mất kết nối với server.")
            client_socket.close()
            break

# Tạo giao diện đăng nhập
def login_screen():
   
    pygame.display.set_caption("Đăng nhập")

    ip_text = ''
    port_text = ''
    message = ''
    input_box_ip = pygame.Rect(600, 150, 200, 32)
    input_box_port = pygame.Rect(600, 210, 200, 32)
    login_button = pygame.Rect(600, 300, 100, 40)
    clock = pygame.time.Clock()
    input_active_ip = False
    input_active_port = False

    while True:
        screen.fill(WHITE)
        ip_label = font.render("IP:", True, BLACK)
        port_label = font.render("Port:", True, BLACK)
        screen.blit(ip_label, (550, 155))
        screen.blit(port_label, (550, 215))

        pygame.draw.rect(screen, GREEN if input_active_ip else BLACK, input_box_ip, 2)
        pygame.draw.rect(screen, GREEN if input_active_port else BLACK, input_box_port, 2)
        pygame.draw.rect(screen, BLACK, login_button)
        login_text = font.render("Login", True, WHITE)
        screen.blit(login_text, (login_button.x + 15, login_button.y + 5))

        ip_surface = font.render(ip_text, True, BLACK)
        port_surface = font.render(port_text, True, BLACK)
        screen.blit(ip_surface, (input_box_ip.x + 5, input_box_ip.y + 5))
        screen.blit(port_surface, (input_box_port.x + 5, input_box_port.y + 5))

        if message:
            msg_surface = font.render(message, True, RED)
            screen.blit(msg_surface, (150, 360))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box_ip.collidepoint(event.pos):
                    input_active_ip = True
                    input_active_port = False
                elif input_box_port.collidepoint(event.pos):
                    input_active_port = True
                    input_active_ip = False
                elif login_button.collidepoint(event.pos):
                    client_socket = connect_to_server(ip_text, port_text)
                    if client_socket:
                        message = "Kết nối thành công! Đang mở game..."
                        pygame.display.update()
                        pygame.time.delay(1000)

                        # Khởi tạo luồng cho việc nhận tin nhắn từ server
                        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
                        receive_thread.daemon = True  # Đảm bảo rằng thread này sẽ kết thúc khi ứng dụng chính đóng
                        receive_thread.start()

                        open_game()
                    else:
                        message = "Kết nối thất bại. Kiểm tra IP và Port."

            elif event.type == pygame.KEYDOWN:
                if input_active_ip:
                    if event.key == pygame.K_BACKSPACE:
                        ip_text = ip_text[:-1]
                    else:
                        ip_text += event.unicode
                elif input_active_port:
                    if event.key == pygame.K_BACKSPACE:
                        port_text = port_text[:-1]
                    else:
                        port_text += event.unicode

        pygame.display.flip()
        clock.tick(30)


def open_game():
    screen.fill(WHITE)
    pygame.display.flip()
    pygame.time.delay(3000)
    coutdown_sound.play()
    show_coutdown(screen,bg_color)
    run_game()


countdown_time = 180
start_ticks = pygame.time.get_ticks()  

# Danh sách viên đạn
bullets = []
max_bullets = 20
bullet_reload_time = 3  # 3 giây
last_reload_time_player1 = pygame.time.get_ticks()
last_reload_time_player2 = pygame.time.get_ticks()

# Thời gian bắn
last_shot_time_player1 = 0
last_shot_time_player2 = 0
cooldown = 6  

# Thanh máu
health1, health2 = 125, 125  # Sức khỏe ban đầu của mỗi nhân vật
avatar1_image = pygame.image.load(f'{assets_path1}/Kaito.jpg')
avatar2_image = pygame.image.load(f'{assets_path1}/Boa.jpg')
dark_mode_image = pygame.image.load(f'{assets_path1}/Anime2.jpg').convert()
dark_mode_image = pygame.transform.scale(dark_mode_image, (WIDTH, HEIGHT))

light_mode_image = pygame.image.load(f'{assets_path1}/Anime3.jpg').convert()
light_mode_image = pygame.transform.scale(light_mode_image, (WIDTH, HEIGHT))

coutdown_sound =  pygame.mixer.Sound(f'{assets_path2}/sound_coutdown.mp3')


is_dark_mode = False
current_image_index = 0
# Vị trí và kích thước của nút dark mode
button_rect = pygame.Rect(WIDTH - 150, 20, 120, 50)

# Hàm kiểm tra va chạm
def check_collision(pos1, pos2, size):
    return (pos1[0] < pos2[0] + size[0] and
            pos1[0] + size[0] > pos2[0] and
            pos1[1] < pos2[1] + size[1] and
            pos1[1] + size[1] > pos2[1])

def draw_health_bars():
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 340, 90, 250, 20))  # Viền thanh máu ở giữa
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 340, 90, health1 * 2, 20))  # Máu hiện tại
    avatar1_scaled = pygame.transform.scale(avatar1_image, (250, 110))  # Kích thước avatar lớn hơn
    screen.blit(avatar1_scaled, (WIDTH // 2 - 600, 0))  # Hiển thị ảnh đại diện gần rìa trái

    pygame.draw.rect(screen, RED, (WIDTH // 2 + 90, 90, 250, 20))  # Viền thanh máu ở giữa
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 + 90, 90, health2 * 2, 20))  # Máu hiện tại
    avatar2_scaled = pygame.transform.scale(avatar2_image, (250, 110))  # Kích thước avatar lớn hơn
    screen.blit(avatar2_scaled, (WIDTH - 480, 0))  # Hiển thị ảnh đại diện gần rìa phải

    elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000  # Thời gian đã trôi qua (giây)
    remaining_time = max(0, countdown_time - elapsed_time)  # Thời gian còn lại
    font = pygame.font.SysFont(None, 48)  # Chọn phông chữ
    time_text = font.render(str(remaining_time), True, WHITE)  # Hiển thị thời gian còn lại
    screen.blit(time_text, (WIDTH // 2 - 20 , 50))  #a Vị trí hiển thị thời gian
    
player1_pos = [100, 300]
player2_pos = [1000, 300]
player_width, player_height = 100, 200  
player_speed = 15

def draw_player(surface, pos, color):
    pygame.draw.rect(surface, color, (pos[0], pos[1] + 40, player_width, player_height - 40))  # Thân
    pygame.draw.circle(surface, color, (pos[0] + player_width // 2, pos[1] + 40), 40)  # Đầu
    pygame.draw.circle(surface, (0, 0, 0), (pos[0] + 24, pos[1] + 30), 10)  # Mắt trái
    pygame.draw.circle(surface, (0, 0, 0), (pos[0] + 76, pos[1] + 30), 10)  # Mắt phải
    pygame.draw.arc(surface, (0, 0, 0), (pos[0] + 20, pos[1] + 40, 40, 20), 0, 3.14, 2)  # Miệng
    pygame.draw.rect(surface, color, (pos[0] - 20, pos[1] + 80, 20, 60))  # Tay trái
    pygame.draw.rect(surface, color, (pos[0] + player_width, pos[1] + 80, 20, 60))  # Tay phải
    pygame.draw.rect(surface, color, (pos[0] + 35, pos[1] + player_height - 20, 20, 20))  # Chân trái
    pygame.draw.rect(surface, color, (pos[0] + 65, pos[1] + player_height - 20, 20, 20))  # Chân phải


def draw_bullet(surface, pos):
    pygame.draw.polygon(surface, BULLET_COLOR, [
        (pos[0], pos[1]),
        (pos[0] + 15, pos[1] + 5),
        (pos[0] + 15, pos[1] - 5)
    ])  
    
def show_coutdown(screen, bg_color):
    FONT_SIZE = 72
    FONT_COLOR = (255, 0, 0) 
    FONT = pygame.font.Font(None, FONT_SIZE)
    countdown_numbers = [3, 2, 1]
    for number in countdown_numbers:
        screen.fill(bg_color) 
        text = FONT.render(str(number), True, FONT_COLOR)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)  
    screen.fill(bg_color) 
    pygame.display.flip()
    
def run_game():
    global is_dark_mode, health1, health2, player1_pos, player2_pos, bullets, last_shot_time_player1, last_shot_time_player2
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    is_dark_mode = not is_dark_mode

        # Lấy trạng thái bàn phím
        keys = pygame.key.get_pressed()

        # Di chuyển nhân vật 1
        new_player1_pos = player1_pos[:]
        if keys[pygame.K_a]:
            new_player1_pos[0] -= player_speed
        if keys[pygame.K_d]:
            new_player1_pos[0] += player_speed
        if keys[pygame.K_w]:
            new_player1_pos[1] -= player_speed
        if keys[pygame.K_s]:
            new_player1_pos[1] += player_speed

        # Kiểm tra va chạm với nhân vật 2
        if not check_collision(new_player1_pos, player2_pos, (player_width, player_height)):
            new_player1_pos[0] = max(0, min(new_player1_pos[0], WIDTH - player_width))
            new_player1_pos[1] = max(0, min(new_player1_pos[1], HEIGHT - player_height))
            player1_pos = new_player1_pos

        # Gửi vị trí của Player 1 tới máy chủ
        client_socket.send(str(player1_pos).encode())

     
        # Di chuyển nhân vật 2
        new_player2_pos = player2_pos[:]
        if keys[pygame.K_LEFT]:
            new_player2_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            new_player2_pos[0] += player_speed
        if keys[pygame.K_UP]:
            new_player2_pos[1] -= player_speed
        if keys[pygame.K_DOWN]:
            new_player2_pos[1] += player_speed

        # Kiểm tra va chạm với nhân vật 1
        if not check_collision(new_player2_pos, player1_pos, (player_width, player_height)):
            new_player2_pos[0] = max(0, min(new_player2_pos[0], WIDTH - player_width))
            new_player2_pos[1] = max(0, min(new_player2_pos[1], HEIGHT - player_height))
            player2_pos = new_player2_pos

        # Gửi vị trí của Player 2 tới máy chủ
        client_socket.send(str(player2_pos).encode())

        # Bắn viên đạn
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and len([b for b in bullets if b[2] == "right"]) < max_bullets:
            if current_time - last_shot_time_player1 >= bullet_reload_time:
                bullets.append([player1_pos[0] + player_width, player1_pos[1] + player_height // 2, "right"])
                last_shot_time_player1 = current_time

        # Kiểm tra thời gian hồi chiêu cho player2
        if keys[pygame.K_RETURN] and len([b for b in bullets if b[2] == "left"]) < max_bullets:
            if current_time - last_shot_time_player2 >= bullet_reload_time:
                bullets.append([player2_pos[0], player2_pos[1] + player_height // 2, "left"])
                last_shot_time_player2 = current_time

        # Cập nhật vị trí viên đạn
        for bullet in bullets[:]:
            if bullet[2] == "right":
                bullet[0] += 15 # Tăng vị trí x cho viên đạn nhân vật 1
            else:
                bullet[0] -= 15  # Giảm vị trí x cho viên đạn nhân vật 2

        
    
            # Kiểm tra va chạm với thanh máu
            if (bullet[0] >= player2_pos[0] and bullet[0] <= player2_pos[0] + player_width and 
                    player2_pos[1] < bullet[1] < player2_pos[1] + player_height):
                health2 -= 5
                bullets.remove(bullet)

            if (bullet[0] >= player1_pos[0] and bullet[0] <= player1_pos[0] + player_width and 
                    player1_pos[1] < bullet[1] < player1_pos[1] + player_height):
                health1 -= 5
                bullets.remove(bullet)



        if is_dark_mode:
                screen.blit(dark_mode_image, (0, 0))
        else:
            screen.blit(light_mode_image, (0, 0))
            
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
        font = pygame.font.SysFont(None, 36)
        button_text = font.render("Dark Mode", True, WHITE)
        screen.blit(button_text, (button_rect.x + 10, button_rect.y + 10))
        draw_health_bars()  # Vẽ thanh máu và avatar
        draw_player(screen, player1_pos, PLAYER1_COLOR)  # Vẽ nhân vật 1
        draw_player(screen, player2_pos, PLAYER2_COLOR)  # Vẽ nhân vật 2
        for bullet in bullets:
            draw_bullet(screen, bullet)  # Vẽ các viên đạn

        pygame.display.flip()  # Cập nhật màn hình
        pygame.time.delay(30)  # Đợi 30ms để điều chỉnh tốc độ khung hình

login_screen()