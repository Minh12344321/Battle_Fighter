import pygame
import sys
import time

# Khởi tạo Pygame
pygame.init()

# Kích thước cửa sổ
WIDTH, HEIGHT = 1600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Đánh Nhau")

# Màu sắc
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BULLET_COLOR = (255, 255, 0)
PLAYER1_COLOR = (255, 255, 0)  # Màu sắc nhân vật 1
PLAYER2_COLOR = (255, 100, 100)  # Màu sắc nhân vật 2
AVATAR1_COLOR = (255, 255, 0)  # Màu sắc avatar cho player 1 (vàng)
AVATAR2_COLOR = (0, 255, 0)     # Màu sắc avatar cho player 2 (xanh lá)

# Thời gian đếm ngược
countdown_time = 300  # 90 giây
start_ticks = pygame.time.get_ticks()  # Thời điểm bắt đầu

# Danh sách viên đạn
bullets = []
max_bullets = 5
bullet_reload_time = 3000  # 3 giây
last_reload_time_player1 = pygame.time.get_ticks()
last_reload_time_player2 = pygame.time.get_ticks()

# Thời gian bắn
last_shot_time_player1 = 0
last_shot_time_player2 = 0
cooldown = 6  # Thời gian hồi chiêu (giây)

# Thanh máu
health1, health2 = 125, 125  # Sức khỏe ban đầu của mỗi nhân vật
avatar1_image = pygame.image.load("Kaito.jpg")
avatar2_image = pygame.image.load("Boa.jpg")
background_image = pygame.image.load("Anime1.jpg").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT)) 
# Hàm kiểm tra va chạm
def check_collision(pos1, pos2, size):
    return (pos1[0] < pos2[0] + size[0] and
            pos1[0] + size[0] > pos2[0] and
            pos1[1] < pos2[1] + size[1] and
            pos1[1] + size[1] > pos2[1])

# Hàm vẽ thanh máu và avatar
def draw_health_bars():
    # Thanh máu nhân vật 1
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 340, 90, 250, 20))  # Viền thanh máu ở giữa
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 340, 90, health1 * 2, 20))  # Máu hiện tại
    # Avatar nhân vật 1
    avatar1_scaled = pygame.transform.scale(avatar1_image, (250, 110))  # Kích thước avatar lớn hơn
    screen.blit(avatar1_scaled, (WIDTH // 2 - 600, 0))  # Hiển thị ảnh đại diện gần rìa trái

    # Thanh máu nhân vật 2
    pygame.draw.rect(screen, RED, (WIDTH // 2 + 90, 90, 250, 20))  # Viền thanh máu ở giữa
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 + 90, 90, health2 * 2, 20))  # Máu hiện tại
    # Avatar nhân vật 2
    avatar2_scaled = pygame.transform.scale(avatar2_image, (250, 110))  # Kích thước avatar lớn hơn
    screen.blit(avatar2_scaled, (WIDTH - 480, 0))  # Hiển thị ảnh đại diện gần rìa phải

    # Hiển thị thời gian đếm ngược
    elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000  # Thời gian đã trôi qua (giây)
    remaining_time = max(0, countdown_time - elapsed_time)  # Thời gian còn lại
    font = pygame.font.SysFont(None, 48)  # Chọn phông chữ
    time_text = font.render(str(remaining_time), True, WHITE)  # Hiển thị thời gian còn lại
    screen.blit(time_text, (WIDTH // 2 - 20 , 50))  # Vị trí hiển thị thời gian
    
# Thông tin nhân vật
player1_pos = [100, 300]
player2_pos = [1000, 300]
player_width, player_height = 100, 200  # Kích thước nhân vật gấp đôi
player_speed = 15

# Hàm vẽ nhân vật
def draw_player(surface, pos, color):
   
    # Vẽ thân hình
    pygame.draw.rect(surface, color, (pos[0], pos[1] + 40, player_width, player_height - 40))  # Thân
    pygame.draw.circle(surface, color, (pos[0] + player_width // 2, pos[1] + 40), 40)  # Đầu
    pygame.draw.circle(surface, (0, 0, 0), (pos[0] + 24, pos[1] + 30), 10)  # Mắt trái
    pygame.draw.circle(surface, (0, 0, 0), (pos[0] + 76, pos[1] + 30), 10)  # Mắt phải
    pygame.draw.arc(surface, (0, 0, 0), (pos[0] + 20, pos[1] + 40, 40, 20), 0, 3.14, 2)  # Miệng
    pygame.draw.rect(surface, color, (pos[0] - 20, pos[1] + 80, 20, 60))  # Tay trái
    pygame.draw.rect(surface, color, (pos[0] + player_width, pos[1] + 80, 20, 60))  # Tay phải
    # Adjusting legs for spacing
    pygame.draw.rect(surface, color, (pos[0] + 35, pos[1] + player_height - 20, 20, 20))  # Chân trái
    pygame.draw.rect(surface, color, (pos[0] + 65, pos[1] + player_height - 20, 20, 20))  # Chân phải


# Hàm vẽ viên đạn
def draw_bullet(surface, pos):
    pygame.draw.polygon(surface, BULLET_COLOR, [
        (pos[0], pos[1]),
        (pos[0] + 15, pos[1] + 5),
        (pos[0] + 15, pos[1] - 5)
    ])  # Vẽ mũi tên

# Vòng lặp chính của game
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

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

    if not check_collision(new_player1_pos, player2_pos, (player_width, player_height)):
        new_player1_pos[0] = max(0, min(new_player1_pos[0], WIDTH - player_width))
        new_player1_pos[1] = max(0, min(new_player1_pos[1], HEIGHT - player_height))
        player1_pos = new_player1_pos

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

    if not check_collision(new_player2_pos, player1_pos, (player_width, player_height)):
        new_player2_pos[0] = max(0, min(new_player2_pos[0], WIDTH - player_width))
        new_player2_pos[1] = max(0, min(new_player2_pos[1], HEIGHT - player_height))
        player2_pos = new_player2_pos

    # Bắn viên đạn
    current_time = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and (current_time - last_shot_time_player1) >= cooldown:
        bullets.append([player1_pos[0] + player_width, player1_pos[1] + player_height // 2, "right"])
        last_shot_time_player1 = current_time
    if keys[pygame.K_RETURN] and (current_time - last_shot_time_player2) >= cooldown:
        bullets.append([player2_pos[0], player2_pos[1] + player_height // 2, "left"])
        last_shot_time_player2 = current_time

    # Cập nhật vị trí viên đạn
    for bullet in bullets[:]:
        if bullet[2] == "right":
            bullet[0] += 10  # Tăng vị trí x cho viên đạn nhân vật 1
        else:
            bullet[0] -= 10  # Giảm vị trí x cho viên đạn nhân vật 2

        # Kiểm tra va chạm với thanh máu
      # Kiểm tra va chạm với thanh máu
        # Kiểm tra va chạm với thanh máu
        if (bullet[0] >= player2_pos[0] and bullet[0] <= player2_pos[0] + player_width and 
                player2_pos[1] < bullet[1] < player2_pos[1] + player_height):
            health2 -= 5
            bullets.remove(bullet)

        if (bullet[0] >= player1_pos[0] and bullet[0] <= player1_pos[0] + player_width and 
                player1_pos[1] < bullet[1] < player1_pos[1] + player_height):
            health1 -= 5
            bullets.remove(bullet)



    # Cập nhật màn hình
    screen.blit(background_image, (0, 0))  # Vẽ hình nền
    draw_health_bars()  # Vẽ thanh máu và avatar
    draw_player(screen, player1_pos, PLAYER1_COLOR)  # Vẽ nhân vật 1
    draw_player(screen, player2_pos, PLAYER2_COLOR)  # Vẽ nhân vật 2
    for bullet in bullets:
        draw_bullet(screen, bullet)  # Vẽ các viên đạn

    pygame.display.flip()  # Cập nhật màn hình
    pygame.time.delay(30)  # Đợi 30ms để điều chỉnh tốc độ khung hình
