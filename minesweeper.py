import pygame
import random
import box_object
from autosolver import Autosolver

# ======================
#        GLOBALS       #
# ======================

AUTOSOLVER = True
autosolver_called = False
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
    (0, -1),          (0, 1),
    (1, -1),  (1, 0), (1, 1)
]

# ======================
#        INIT       #
# ======================

board = [[box_object.Box() for _ in range(HEIGHT)] for _ in range(WIDTH)]

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
autosolver_moves = []
autosolver_index = 0
autosolver = Autosolver()
is_first_click = True

# ======================
#      DRAW FUNCS      #
# ======================

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

def draw_mine(x, y):
    center = (x * BOX_SIZE + BOX_SIZE // 2, y * BOX_SIZE + 60 + BOX_SIZE // 2)
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

def draw_flags_left():
    center_x = screen_width // 2
    center_y = 30 

    flags_left_surface = message_font.render(f"Flags: {flags_left}", True, (0, 0, 0))
    flags_left_rect = flags_left_surface.get_rect(center=(center_x, center_y))
    screen.blit(flags_left_surface, flags_left_rect)
    
def draw_flag(x, y):
    flag_center = (x * BOX_SIZE + BOX_SIZE // 2, y * BOX_SIZE + 60 + BOX_SIZE // 2)
    flag_radius = BOX_SIZE // 4

    line_start = (flag_center[0] + flag_radius - 2, flag_center[1] + 5)
    pygame.draw.line(screen, (0, 0, 0), line_start, (line_start[0], line_start[1] - flag_radius - 2), 2)
    pygame.draw.rect(screen, (255, 0, 0), (flag_center[0] - flag_radius, flag_center[1] - flag_radius, 2 * flag_radius, flag_radius))

def draw_timer(elapsed_seconds):
    timer_text = f"{999 if elapsed_seconds > 999 else elapsed_seconds:03}"
    timer_surface = message_font.render(timer_text, True, (0, 0, 0))
    timer_rect = timer_surface.get_rect(topright=(screen_width - 10, 10))
    screen.blit(timer_surface, timer_rect)

def draw_board():
    for x in range(WIDTH):
        for y in range(HEIGHT):
            rect = pygame.Rect(x * BOX_SIZE, y * BOX_SIZE + 60, BOX_SIZE, BOX_SIZE)
            pygame.draw.rect(screen, LINE_COLOR, rect, LINE_WIDTH)

            board_item = board[x][y]
            
            if board_item.is_covered:
                pygame.draw.rect(screen, (200, 200, 200), rect)

                outline_rect = rect.inflate(4, 4)  
                pygame.draw.rect(screen, (0, 0, 0), outline_rect, 1)
                if board_item.has_flag:
                    draw_flag(x, y)
            else:
                if board_item.get_content() == 'Mine':
                    draw_mine(x, y)

                mine_count = board_item.get_mine_neighbor_count()
                if mine_count > 0 and not board_item.is_mine():
                    print_mine_neighbor_count(x, y, mine_count)

# ======================
#      GAME LOGIC      #
# ======================

def print_mine_neighbor_count(x, y, mine_count):
    center_x = x * BOX_SIZE + BOX_SIZE // 2
    center_y = y * BOX_SIZE + 60 + BOX_SIZE // 2

    color = get_font_color(mine_count)
    draw_text(str(mine_count), number_font, color, center_x - 10, center_y - 10)

def place_mines():
    global mine_positions
    mine_positions = [] 
    mines = 99
    while mines > 0:
        rand_x = random.randint(0, WIDTH - 1) 
        rand_y = random.randint(0, HEIGHT - 1)  
        if (board[rand_x][rand_y].get_content() != 'Mine'):
            board[rand_x][rand_y].fill_with_mine()
            mine_positions.append((rand_x, rand_y))
            for dx, dy in NEIGHBOR_OFFSETS:
                nx, ny = rand_x + dx, rand_y + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and board[nx][ny].get_content() != 'Mine':
                    board[nx][ny].increment_mine_neighbor_count()
            mines -= 1

def uncover_tile(x, y):
    if is_first_click:
        handle_first_click(x, y)
    if board[x][y].is_covered and not board[x][y].is_mine():
        board[x][y].uncover()
        if board[x][y].get_content() is None and board[x][y].get_mine_neighbor_count() == 0:
            for dx, dy in NEIGHBOR_OFFSETS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                    uncover_tile(nx, ny)

def handle_first_click(click_row, click_col):
    global is_first_click
    is_first_click = False

    found_replacement = False
    new_location = None
    while not found_replacement:
        rand_x = random.randint(0, WIDTH - 1)
        rand_y = random.randint(0, HEIGHT - 1)
        new_location = board[rand_x][rand_y]
        if not new_location.is_mine() and (rand_x, rand_y) != (click_row, click_col):
            found_replacement = True

    board[click_row][click_col].content = None
    if (click_row, click_col) in mine_positions:
        mine_positions.remove((click_row, click_col))
        for dx, dy in NEIGHBOR_OFFSETS:
            nx, ny = click_row + dx, click_col + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                if board[nx][ny].is_mine():
                    board[click_row][click_col].set_number()
                    board[click_row][click_col].increment_mine_neighbor_count()
                board[nx][ny].decrement_mine_neighbor_count()

        new_location.fill_with_mine()
        mine_positions.append((rand_x, rand_y))

        for dx, dy in NEIGHBOR_OFFSETS:
            nx, ny = rand_x + dx, rand_y + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                board[nx][ny].increment_mine_neighbor_count()

    for x in range(WIDTH):
        for y in range(HEIGHT):
            if board[x][y].get_mine_neighbor_count() > 0 and not board[x][y].is_mine():
                board[x][y].set_number()
                print_mine_neighbor_count(x, y, board[x][y].get_mine_neighbor_count())

    if AUTOSOLVER:
       global autosolver_moves
       autosolver_moves.extend(autosolver.solve(board))

def clear_board():
    global board, mine_positions
    board = [[box_object.Box() for _ in range(HEIGHT)] for _ in range(WIDTH)]
    mine_positions = []

def get_mouse_box_pos():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_y -= 60 
    x = mouse_x // BOX_SIZE
    y = mouse_y // BOX_SIZE
    return x, y 

def toggle_flag(x, y):
    global flags_left
    box = board[x][y]
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
        x, y = mine_positions[mine_reveal_index]
        if not board[x][y].has_flag:
            board[x][y].uncover()

        draw_board()
        
        mine_reveal_index += 1
    else:
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if (x, y) not in mine_positions and board[x][y].has_flag:
                    board[x][y].uncover()
                    rect = pygame.Rect(x * BOX_SIZE, y * BOX_SIZE + 60, BOX_SIZE, BOX_SIZE)
                    pygame.draw.rect(screen, (255, 0, 0), rect)
        pygame.display.update()

def restart(reveal=False):
    global game_over, mine_reveal_index, new_game, flags_left, autosolver_called, autosolver_index, autosolver_moves, is_first_click
    game_over = False
    mine_reveal_index = 0
    new_game = True
    if reveal:
        clear_board()
        place_mines()
        flags_left = 99
    autosolver_called = False
    autosolver_moves = []
    autosolver_index = 0
    is_first_click = True
    autosolver.clear_moves()
    draw_board()
    if reveal:
        pygame.display.flip()

def check_quit(event):
    global running
    if event.type == pygame.QUIT:
        running = False

def simulate_mouse_click(x, y, button=1):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT: 
        if button == 1:  
            if board[x][y].is_mine():
                global game_over
                game_over = True
                reveal_mines()
            else:
                uncover_tile(x, y)
        elif button == 3: 
            toggle_flag(x, y)

def show_initial_screen():
    global AUTOSOLVER, running
    screen.fill((200, 200, 200))
    
    title_text = "Enable Autosolver?"
    yes_text = "Press Y for Yes"
    no_text = "Press N for No"

    draw_text(title_text, font, (0, 0, 0), screen_width // 2 - 250, screen_height // 2 - 60)
    draw_text(yes_text, message_font, (0, 0, 0), screen_width // 2 - 100, screen_height // 2)
    draw_text(no_text, message_font, (0, 0, 0), screen_width // 2 - 100, screen_height // 2 + 40)

    pygame.display.flip()
    
    waiting_for_choice = True
    while waiting_for_choice:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  
                waiting_for_choice = False
                AUTOSOLVER = False
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y: 
                    AUTOSOLVER = True
                    waiting_for_choice = False
                elif event.key == pygame.K_n: 
                    AUTOSOLVER = False
                    waiting_for_choice = False

if __name__ == '__main__':
    while running:
        if new_game:
            show_initial_screen()
            clear_board()
            place_mines()
            flags_left = 99
            new_game = False
            you_win = False
            game_over = False
            mine_reveal_index = 0
            autosolver_called = False
            is_first_click = True
            autosolver.clear_moves()
            autosolver_moves = []
            autosolver_index = 0
            start_time = pygame.time.get_ticks()
        
        if AUTOSOLVER and not game_over and not autosolver_moves:
            autosolver_moves.append(autosolver.send_first_move())
            autosolver_index = 0
        
        if AUTOSOLVER and autosolver_moves and not game_over:
            if autosolver_index < len(autosolver_moves):
                x, y, action = autosolver_moves[autosolver_index]
                simulate_mouse_click(x, y, button=1 if action == "uncover" else 3)
                autosolver_index += 1
            
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
                        restart(reveal=True)
                    elif game_over:
                        restart()
                elif event.key == pygame.K_a and not AUTOSOLVER and not autosolver_called:
                    AUTOSOLVER = True
                    autosolver_called = True

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
                        waiting = False
                        break
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        restart()
        else:
            draw_board()
        draw_flags_left()
        draw_timer(elapsed_seconds)
        pygame.display.flip()
        
        clock.tick(30)