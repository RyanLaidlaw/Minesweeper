import pygame
import random
import boxModel

WIDTH = 30
HEIGHT = 16  
BOX_SIZE = 40  
LINE_COLOR = (0, 0, 0)
LINE_WIDTH = 1
NUMBER_OF_BOXES = WIDTH * HEIGHT
screen_width = WIDTH * BOX_SIZE
screen_height = HEIGHT * BOX_SIZE
ONE_COLOR = (0, 0, 255)
TWO_COLOR = (0, 175, 0)
THREE_COLOR = (255, 0, 0)
FOUR_COLOR = (0, 0, 139)
FIVE_COLOR = (139, 0, 0)
SIX_COLOR = (0, 255, 255)
SEVEN_COLOR = (0, 0, 0)
EIGHT_COLOR = (169, 169, 169)

NEIGHBOR_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),         (0, 1),
    (1, -1), (1, 0), (1, 1)
]

board = [[boxModel.Box() for _ in range(WIDTH)] for _ in range(HEIGHT)]
pygame.font.init()
pygame.display.set_caption("Minesweeper")
font = pygame.font.Font(None, 74)
number_font = pygame.font.Font(None, BOX_SIZE)
message_font = pygame.font.Font(None, 36)

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height + 60))
clock = pygame.time.Clock()
running = True
game_over = False
new_game = True
flags_left = 99
mine_reveal_index = 0

def get_font_color(mine_count):
    color_map = {
        1: ONE_COLOR,
        2: TWO_COLOR,
        3: THREE_COLOR,
        4: FOUR_COLOR,
        5: FIVE_COLOR,
        6: SIX_COLOR,
        8: EIGHT_COLOR
    }

    return color_map.get(mine_count, (0, 0, 0))

def draw_board():
    for row in range(HEIGHT):
        for col in range(WIDTH):
            rect = pygame.Rect(col * BOX_SIZE, row * BOX_SIZE + 60, BOX_SIZE, BOX_SIZE)
            pygame.draw.rect(screen, LINE_COLOR, rect, LINE_WIDTH)

            board_item = board[row][col]
            
            if board[row][col].is_covered:
                pygame.draw.rect(screen, (200, 200, 200), rect)

                outline_rect = rect.inflate(4, 4)  
                pygame.draw.rect(screen, (0, 0, 0), outline_rect, 1)
                if board_item.has_flag:
                    draw_flag(row, col)
            else:
                if board_item.get_content() == 'Mine':
                    draw_mine(row, col)

                mine_count = board_item.get_mine_neighbor_count()
                if mine_count > 0 and not board_item.is_mine():
                    print_mine_neighbor_count(row, col, mine_count)

def print_mine_neighbor_count(x, y, mine_count):
    center_x = y * BOX_SIZE + BOX_SIZE // 2
    center_y = x * BOX_SIZE + 60 + BOX_SIZE // 2

    color = get_font_color(mine_count)
    draw_text(str(mine_count), number_font, color, center_x - 10, center_y - 10)

def place_mines():
    global mine_positions
    mine_positions = [] 
    mines = 99
    while mines > 0:
        rand_x = random.randint(0, HEIGHT - 1)
        rand_y = random.randint(0, WIDTH - 1)
        if (board[rand_x][rand_y].get_content() != 'Mine'):
            board[rand_x][rand_y].fill_with_mine()
            mine_positions.append((rand_x, rand_y))
            for dx, dy in NEIGHBOR_OFFSETS:
                nx, ny = rand_x + dx, rand_y + dy
                if 0 <= nx < HEIGHT and 0 <= ny < WIDTH and board[nx][ny].get_content() != 'Mine':
                    board[nx][ny].increment_mine_neighbor_count()
            mines -= 1
    
    for row in range(HEIGHT):
        for col in range(WIDTH):
            mine_count = board[row][col].get_mine_neighbor_count()
            if mine_count > 0 and not board[row][col].is_mine():
                print_mine_neighbor_count(row, col, mine_count)

def uncover_tile(row, col):
    if board[row][col].is_covered: 
        board[row][col].uncover() 
        
        if board[row][col].get_content() == None and board[row][col].get_mine_neighbor_count() == 0:
            for dx, dy in NEIGHBOR_OFFSETS:
                nx, ny = row + dx, col + dy
                if 0 <= nx < HEIGHT and 0 <= ny < WIDTH:
                    uncover_tile(nx, ny)

def clear_board():
    global board, mine_positions
    board = [[boxModel.Box() for _ in range(WIDTH)] for _ in range(HEIGHT)]
    mine_positions = []

def draw_mine(x, y):
    center = (y * BOX_SIZE + BOX_SIZE // 2, x * BOX_SIZE + 60 + BOX_SIZE // 2)
    radius = BOX_SIZE // 4
    pygame.draw.circle(screen, (0, 0, 0), center, radius)

def draw_text(text: str, font: pygame.font.Font, color: tuple, x: int, y: int):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_game_over(win=False):
    center_y = 30
    game_over_pos = 80

    if win:
        you_win_surface = message_font.render("You Win!", True, (0, 0, 0))
        game_over_rect = you_win_surface.get_rect(center=(game_over_pos - 10, center_y))
        screen.blit(you_win_surface, game_over_rect)
    else:
        game_over_surface = message_font.render("Game Over!", True, (0, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=(game_over_pos, center_y))
        screen.blit(game_over_surface, game_over_rect)

    restart_surface = message_font.render("Press Enter to Restart.", True, (0, 0, 0))
    restart_rect = restart_surface.get_rect(center=(game_over_pos + 250, center_y))
    screen.blit(restart_surface, restart_rect)

def get_mouse_box_pos():
    x, y = pygame.mouse.get_pos()
    y -= 60
    col = x // BOX_SIZE
    row = y // BOX_SIZE
    return row, col

def draw_flags_left():
    center_x = screen_width // 2
    center_y = 30 

    flags_left_surface = message_font.render(f"Flags: {flags_left}", True, (0, 0, 0))
    flags_left_rect = flags_left_surface.get_rect(center=(center_x, center_y))
    screen.blit(flags_left_surface, flags_left_rect)
    
def draw_flag(row, col):
    flag_center = (col * BOX_SIZE + BOX_SIZE // 2, row * BOX_SIZE + 60 + BOX_SIZE // 2)
    flag_radius = BOX_SIZE // 4

    line_start = (flag_center[0] + flag_radius - 2, flag_center[1] + 5)
    pygame.draw.line(screen, (0, 0, 0), line_start, (line_start[0], line_start[1] - flag_radius - 2), 2)
    pygame.draw.rect(screen, (255, 0, 0), (flag_center[0] - flag_radius, flag_center[1] - flag_radius, 2 * flag_radius, flag_radius))

def toggle_flag(row, col):
    global flags_left
    box = board[row][col]
    if box.is_covered:
        if not box.has_flag:
            box.set_flag(True)
            flags_left -= 1
        else:
            box.set_flag(False)
            flags_left += 1   

def reveal_mines():
    global mine_reveal_index 

    if mine_reveal_index < len(mine_positions):
        row, col = mine_positions[mine_reveal_index]
        if not board[row][col].has_flag:
            board[row][col].uncover()

        draw_board()
        
        mine_reveal_index += 1
    else:
        for row in range(HEIGHT):
            for col in range(WIDTH):
                if (row, col) not in mine_positions and board[row][col].has_flag:
                    board[row][col].uncover()
                    rect = pygame.Rect(col * BOX_SIZE, row * BOX_SIZE + 60, BOX_SIZE, BOX_SIZE)
                    pygame.draw.rect(screen, (255, 0, 0), rect)
        pygame.display.update()

def restart():
    global game_over, mine_reveal_index, new_game, waiting
    game_over = False
    mine_reveal_index = 0
    new_game = True
    draw_board()

def check_quit(event):
    global running
    if event.type == pygame.QUIT:
        running = False
    
def restart_during_reveal():
    global game_over, mine_reveal_index, new_game, flags_left
    game_over = False
    mine_reveal_index = 0
    new_game = True
    clear_board()
    place_mines()
    flags_left = 99
    draw_board()
    pygame.display.flip()

def draw_timer(elapsed_seconds):
    timer_text = f"{999 if elapsed_seconds > 999 else elapsed_seconds:03}"
    timer_surface = message_font.render(timer_text, True, (0, 0, 0))
    timer_rect = timer_surface.get_rect(topright=(screen_width - 10, 10))
    screen.blit(timer_surface, timer_rect)

while running:
    if new_game:
        clear_board()
        place_mines()
        flags_left = 99
        new_game = False
        you_win = False
        game_over = False
        mine_reveal_index = 0
        start_time = pygame.time.get_ticks()
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            row, col = get_mouse_box_pos()
            board_item = board[row][col]
            if event.button == 3:
                toggle_flag(row, col)
            else: 
                if not board_item.has_flag:
                    uncover_tile(row, col)
                    if board_item.get_content() == 'Mine':
                        game_over = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if game_over and mine_reveal_index < len(mine_positions):
                    restart_during_reveal()
                elif game_over:
                    restart()

    if flags_left == 0:
        game_over = True
        you_win = True
    
    elapsed_time = pygame.time.get_ticks() - start_time 
    elapsed_seconds = elapsed_time // 1000 
    
    screen.fill("white")
    if game_over:
        reveal_mines()
        draw_game_over() if not you_win else draw_game_over(you_win)
        pygame.event.clear()
        if mine_reveal_index >= len(mine_positions):
            reveal_mines()
            waiting = True
            while waiting:
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    restart()
                    waiting = False
                elif event.type == pygame.QUIT:
                    running = False
            check_quit(event)
        else:
            for event in pygame.event.get():
                check_quit(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    restart()
    else:
        draw_board()
    draw_flags_left()
    draw_timer(elapsed_seconds)
    pygame.display.flip()
    
    clock.tick(30)