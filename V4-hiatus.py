import pygame, time, random, copy

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1400, 800
GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT = 800, 800
INPUT_MAP_SIZE = 4
GAME_MAP_SIZE = 8
TILE_SIZE_W = int(GAME_SCREEN_WIDTH / GAME_MAP_SIZE)
TILE_SIZE_H = int(GAME_SCREEN_HEIGHT / GAME_MAP_SIZE)
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def blank_map(size):
    empty_map = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(0)
        empty_map.append(row)
    return empty_map

def draw_map(map, width, height, png=False):
    canvas = pygame.Surface((width*TILE_SIZE_W, height*TILE_SIZE_H))
    canvas.set_colorkey((0, 0, 0))
    for row in range(height):
        for column in range(width):
            if map[row][column]%2 == 0 and not png:
                color = (0, 40, 75) 
            elif map[row][column]%2 != 0:
                color = (0, 0, 50)
            else:
                color = (0, 0, 0) #transparent because of colorkey
            pygame.draw.rect(canvas, color, (column * TILE_SIZE_W, row * TILE_SIZE_H, TILE_SIZE_W-1, TILE_SIZE_H-1))    
    return canvas

def update_click():
    x, y = pygame.mouse.get_pos()
    if x >= GAME_SCREEN_WIDTH+TILE_SIZE_W and x <= SCREEN_WIDTH-TILE_SIZE_W and y >= 200 and y <= 600: 
        column = int(x/TILE_SIZE_W)-9
        row = int(y/TILE_SIZE_H)-2
        input_map[row][column] += 1

def combo_clear(map, SIZE, clear_value, sizing=False):
    clear_list = []
    max_width = 0
    min_width = 100
    for row_num, row in enumerate(map):
        filling = 0
        for column_num, column_value in enumerate(row):
            if column_value%2 != clear_value:
                filling += 1
                max_width = max(max_width, column_num)
                min_width = min(min_width, column_num)
        if filling == SIZE:
            for column_num, column in enumerate(row):
                clear_list.append((row_num, column_num)) 
    width = max_width-min_width+1

    #this is a bit more complicated cause the column values are all in seperate lists :(
    max_height = 0
    min_height = 100
    column_fillings = []
    for i in range(SIZE):
        column_fillings.append(0)

    for row_num, row in enumerate(map):
        for column_num, column_value in enumerate(map[row_num]):
            if column_value%2 != clear_value:
                column_fillings[column_num] += 1
                max_height = max(max_height, row_num)
                min_height = min(min_height, row_num)

    for column_num, filling in enumerate(column_fillings):
        if filling == SIZE:
            for row_num, row in enumerate(map):
                clear_list.append((row_num, column_num))
    height = max_height-min_height+1

    if not sizing:
        clear_list = list(dict.fromkeys(clear_list))
        return clear_list
    else:
        return width, height

def render():   
    window.blit(draw_map(game_map, GAME_MAP_SIZE, GAME_MAP_SIZE), (0, 0))
    window.blit(draw_map(input_map, INPUT_MAP_SIZE, INPUT_MAP_SIZE), (900, 200))
    if placing:
        window.blit(draw_map(piece_map, piece_w, piece_h, png=True), (piece_x, piece_y))
    pygame.display.update()

def generate_piece():
    piece_map = copy.deepcopy(input_map)
    clear_list = combo_clear(input_map, INPUT_MAP_SIZE, 1)
    clear_list = sorted(clear_list, reverse=True)
    for row, column in clear_list:
        del piece_map[row][column]
    
    clear_list = []
    for row_num, row in enumerate(piece_map):
        if row == []:
            clear_list.append(row_num)
    clear_list = sorted(clear_list, reverse=True)
    for row_num in clear_list:
        piece_map.pop(row_num) 
            
    piece_w, piece_h = combo_clear(input_map, INPUT_MAP_SIZE, 0, sizing=True)
    return piece_map, piece_w, piece_h

def legal_move(x, y):
    if piece_y+y*TILE_SIZE_H > -1 and piece_y+(y+piece_h-1)*TILE_SIZE_H < TILE_SIZE_H*(GAME_MAP_SIZE):
        if piece_x+x*TILE_SIZE_W > -1 and piece_x+(x+piece_w-1)*TILE_SIZE_W < TILE_SIZE_W*(GAME_MAP_SIZE):
            return True
    return False

def place_piece():
    placement = []
    for row_num, row in enumerate(piece_map):
        for column_num, column in enumerate(piece_map[row_num]):
            if piece_map[row_num][column_num]%2 == 1:
                target_row = row_num+int(piece_y/TILE_SIZE_H)
                target_column = column_num+int(piece_x/TILE_SIZE_W)
                if game_map[target_row][target_column]%2 != 1:
                    placement.append((target_row, target_column))
                else:
                    return False
    for row, column in placement:
        game_map[row][column] = 1
    return True

game_map = blank_map(GAME_MAP_SIZE)
input_map = blank_map(INPUT_MAP_SIZE)
running = True
placing = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not placing:
            update_click()
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not last_keys[pygame.K_SPACE]:
        if not placing:
            placing = True
            piece_map, piece_w, piece_h = generate_piece()
            piece_x, piece_y = 0, 0
        elif placing:
            if place_piece():
                placing = False
                input_map = blank_map(INPUT_MAP_SIZE)
                clear_list = combo_clear(game_map, GAME_MAP_SIZE, 0)
                if clear_list:
                    time.sleep(0.3)
                    for row, column in clear_list:
                        game_map[row][column] = 0

    elif placing:
        if keys[pygame.K_w] and not last_keys[pygame.K_w] and legal_move(0, -1):
            piece_y -= TILE_SIZE_H
        if keys[pygame.K_s] and not last_keys[pygame.K_s] and legal_move(0, 1):
            piece_y += TILE_SIZE_H
        if keys[pygame.K_a] and not last_keys[pygame.K_a] and legal_move(-1, 0):
            piece_x -= TILE_SIZE_W
        if keys[pygame.K_d] and not last_keys[pygame.K_d] and legal_move(1, 0):
            piece_x += TILE_SIZE_W
        
    render()
    last_keys = keys
