import pygame
import sys
import time
import socket
import os
import threading,inspect,json

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
assets_path1 = os.path.join(currentdir, 'Assets', 'Images')
assets_path2 = os.path.join(currentdir, 'Assets', 'Sound')
pygame.init()

client_socket = None

WIDTH, HEIGHT = 1600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Fighter")
font = pygame.font.Font(None, 32)

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

BULLET_COLOR = (255, 255, 0)
PLAYER1_COLOR = (255, 255, 0) 
PLAYER2_COLOR = (255, 100, 100)  
AVATAR1_COLOR = (255, 255, 0)  
AVATAR2_COLOR = GREEN   
BUTTON_COLOR = BLACK
bg_color = WHITE

HOST = '127.0.0.1'  
PORT = 12345        

# Tạo hàm kết nối socket
def connect_to_server(ip, port):
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, int(port)))
        return client_socket
    except Exception as e:
        print("Error:", e)
        return None 
    

# Function to receive and process messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print("Received from server:", message)  
        except:
            print("Lost connection to the server.")
            client_socket.close()
            break
        
def login_screen():
    pygame.display.set_caption("Login")
    ip_text = ''
    port_text = ''
    message = ''
    input_box_ip = pygame.Rect(600, 150, 200, 32)
    input_box_port = pygame.Rect(600, 210, 200, 32)
    login_button = pygame.Rect(600, 300, 100, 40)
    clock = pygame.time.Clock()
    input_active_ip = False
    input_active_port = False
    client_socket = None 

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
                elif login_button.collidepoint(event.pos) and not client_socket:
                    client_socket = connect_to_server(ip_text, port_text)
                    if client_socket:
                        message = "Connected successfully"
                        pygame.display.update()
                        pygame.time.delay(1000)

                        # Bắt đầu luồng để nhận tin nhắn
                        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
                        receive_thread.daemon = True  
                        receive_thread.start()

                        run_game()  # Chạy trò chơi
                    else:
                        message = "Error connection.Check again IP and Port."

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

countdown_time = 180
start_ticks = pygame.time.get_ticks()  

bullets = []
max_bullets = 20
bullet_reload_time = 3  
last_reload_time_player1 = pygame.time.get_ticks()
last_reload_time_player2 = pygame.time.get_ticks()

last_shot_time_player1 = 0
last_shot_time_player2 = 0
cooldown = 6  

health1, health2 = 125, 125  
avatar1_image = pygame.image.load(f'{assets_path1}/Kaito.jpg')
avatar2_image = pygame.image.load(f'{assets_path1}/Boa.jpg')
dark_mode_image = pygame.image.load(f'{assets_path1}/Anime2.jpg').convert()
dark_mode_image = pygame.transform.scale(dark_mode_image, (WIDTH, HEIGHT))

light_mode_image = pygame.image.load(f'{assets_path1}/Anime3.jpg').convert()
light_mode_image = pygame.transform.scale(light_mode_image, (WIDTH, HEIGHT))

coutdown_sound =  pygame.mixer.Sound(f'{assets_path2}/sound_coutdown.mp3')
bullet_hit_sound = pygame.mixer.Sound(f'{assets_path2}/pistol_shot.mp3')
punch_sound = pygame.mixer.Sound(f'{assets_path2}/punch.mp3')


is_dark_mode = False
current_image_index = 0
button_rect = pygame.Rect(WIDTH - 150, 20, 120, 50)

def check_collision(pos1, pos2, size):
    return (pos1[0] < pos2[0] + size[0] and
            pos1[0] + size[0] > pos2[0] and
            pos1[1] < pos2[1] + size[1] and
            pos1[1] + size[1] > pos2[1])

def draw_health_bars():
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 340, 90, 250, 20))  
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 340, 90, health1 * 2, 20))  
    avatar1_scaled = pygame.transform.scale(avatar1_image, (250, 110)) 
    screen.blit(avatar1_scaled, (WIDTH // 2 - 600, 0))  

    pygame.draw.rect(screen, RED, (WIDTH // 2 + 90, 90, 250, 20)) 
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 + 90, 90, health2 * 2, 20))  
    avatar2_scaled = pygame.transform.scale(avatar2_image, (250, 110))  
    screen.blit(avatar2_scaled, (WIDTH - 480, 0)) 

    elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000  
    remaining_time = max(0, countdown_time - elapsed_time)  
    font = pygame.font.SysFont(None, 48) 
    time_text = font.render(str(remaining_time), True, WHITE)  
    screen.blit(time_text, (WIDTH // 2 - 20 , 50)) 
    
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
    
def display_winner(winner):
    font = pygame.font.SysFont(None, 74)
    text = font.render(f"{winner} Wins!", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()

    
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

def show_play_again_form():
    form_x = (WIDTH - 300) // 2
    form_y = (HEIGHT - 200) // 2
    font = pygame.font.SysFont(None, 36)
    while True:
        screen.fill(BLACK)  
        pygame.draw.rect(screen, WHITE, (form_x, form_y, 300,200))  # Nền của form
        text = font.render("Play Again?", True, BLACK)
        screen.blit(text, (form_x + (300 - text.get_width()) // 2, form_y + 30))
        yes_button = pygame.Rect(form_x + 40, form_y + 120, 80, 40)
        no_button = pygame.Rect(form_x + 180, form_y + 120, 80, 40)
        pygame.draw.rect(screen, RED, yes_button)
        pygame.draw.rect(screen, RED, no_button)
        yes_text = font.render("Yes", True, WHITE)
        no_text = font.render("No", True, WHITE)
        screen.blit(yes_text, (yes_button.x + (yes_button.width - yes_text.get_width()) // 2,
                               yes_button.y + (yes_button.height - yes_text.get_height()) // 2))
        screen.blit(no_text, (no_button.x + (no_button.width - no_text.get_width()) // 2,
                              no_button.y + (no_button.height - no_text.get_height()) // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.collidepoint(event.pos):
                    open_game() 
                elif no_button.collidepoint(event.pos):
                    login_screen()
                    return
    
def send_position(client_socket, player_id, position):
    try:
        message = f"{player_id}:{position[0]},{position[1]}"
        client_socket.send(message.encode())
    except Exception as e:
        print("Lỗi khi gửi vị trí:", e)

    
def reset_game_state():
    global health1, health2, player1_pos, player2_pos, bullets, last_shot_time_player1, last_shot_time_player2
    health1 = 125
    health2 = 125
    player1_pos = [100, 300]  
    player2_pos = [1100, 300] 
    bullets = []
    last_shot_time_player1 = 0
    last_shot_time_player2 = 0

def open_game():
    reset_game_state()
    screen.fill(WHITE)
    pygame.display.flip()
    run_game()
    

def run_game():
    global is_dark_mode, health1, health2, player1_pos, player2_pos, bullets, last_shot_time_player1, last_shot_time_player2,client_socket
    prev_player1_pos = player1_pos[:]
    prev_player2_pos = player2_pos[:]
    
    screen.fill(WHITE)
    pygame.display.flip()
    coutdown_sound.play()
    show_coutdown(screen,bg_color)
   
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    is_dark_mode = not is_dark_mode
        keys = pygame.key.get_pressed()

        new_player1_pos = player1_pos[:]
        if keys[pygame.K_a]:
            new_player1_pos[0] -= player_speed
        if keys[pygame.K_d]:
            new_player1_pos[0] += player_speed
        if keys[pygame.K_w]:
            new_player1_pos[1] -= player_speed
        if keys[pygame.K_s]:
            new_player1_pos[1] += player_speed

        if not check_collision(new_player1_pos, player2_pos, (player_width, player_height)):
            new_player1_pos[0] = max(0, min(new_player1_pos[0], WIDTH - player_width))
            new_player1_pos[1] = max(0, min(new_player1_pos[1], HEIGHT - player_height))
            # Gửi vị trí nếu thay đổi
            if new_player1_pos != prev_player1_pos:
                player1_pos = new_player1_pos
                prev_player1_pos = new_player1_pos[:]
                send_position(client_socket, 1, player1_pos)
            
            
   
        new_player2_pos = player2_pos[:]
        if keys[pygame.K_LEFT]:
            new_player2_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            new_player2_pos[0] += player_speed
        if keys[pygame.K_UP]:
            new_player2_pos[1] -= player_speed
        if keys[pygame.K_DOWN]:
            new_player2_pos[1] += player_speed

        if not check_collision(new_player2_pos, player1_pos, (player_width, player_height)):
            new_player2_pos[0] = max(0, min(new_player2_pos[0], WIDTH - player_width))
            new_player2_pos[1] = max(0, min(new_player2_pos[1], HEIGHT - player_height))
            player2_pos = new_player2_pos
            
            if new_player2_pos != prev_player2_pos:
                player2_pos = new_player2_pos
                prev_player2_pos = new_player2_pos[:]
                send_position(client_socket, 2, player2_pos)

            
        if health1 <= 0 or health2 <= 0:
            winner = "Player 2" if health1 <= 0 else "Player 1"
            display_winner(winner)  
            pygame.time.delay(3000)
            show_play_again_form()
            running = False
           
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and len([b for b in bullets if b[2] == "right"]) < max_bullets:
            bullet_hit_sound.play() 

            if current_time - last_shot_time_player1 >= bullet_reload_time:
                bullets.append([player1_pos[0] + player_width, player1_pos[1] + player_height // 2, "right"])
                last_shot_time_player1 = current_time

        if keys[pygame.K_RETURN] and len([b for b in bullets if b[2] == "left"]) < max_bullets:
            bullet_hit_sound.play() 

            if current_time - last_shot_time_player2 >= bullet_reload_time:
                bullets.append([player2_pos[0], player2_pos[1] + player_height // 2, "left"])
                last_shot_time_player2 = current_time

        for bullet in bullets[:]:
            if bullet[2] == "right":
                bullet[0] += 15 
            else:
                bullet[0] -= 15 

            if (bullet[0] >= player2_pos[0] and bullet[0] <= player2_pos[0] + player_width and 
                    player2_pos[1] < bullet[1] < player2_pos[1] + player_height):
                health2 -= 5
                bullets.remove(bullet)
                punch_sound.play()
               
            if (bullet[0] >= player1_pos[0] and bullet[0] <= player1_pos[0] + player_width and 
                    player1_pos[1] < bullet[1] < player1_pos[1] + player_height):
                health1 -= 5
                bullets.remove(bullet)
                punch_sound.play()

        if is_dark_mode:
                screen.blit(dark_mode_image, (0, 0))
        else:
            screen.blit(light_mode_image, (0, 0))
            
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
        font = pygame.font.SysFont(None, 36)
        button_text = font.render("Dark Mode", True, WHITE)
        screen.blit(button_text, (button_rect.x + 10, button_rect.y + 10))
        draw_health_bars()  
        draw_player(screen, player1_pos, PLAYER1_COLOR)  
        draw_player(screen, player2_pos, PLAYER2_COLOR) 
        for bullet in bullets:
            draw_bullet(screen, bullet)  

        pygame.display.flip()  
        pygame.time.delay(30)  

login_screen()