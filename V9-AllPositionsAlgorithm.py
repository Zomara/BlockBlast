import pygame, time, random, copy, sys
from itertools import permutations 

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 800
GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT = 800, 800
INPUT_MAP_SIZE = 5
GAME_MAP_SIZE = 8
TILE_SIZE_W = int(GAME_SCREEN_WIDTH / GAME_MAP_SIZE)
TILE_SIZE_H = int(GAME_SCREEN_HEIGHT / GAME_MAP_SIZE)
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#0 / even = empty
#1 / odd = filled

def blank_map(size):
    empty_map = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append((0, (100, 100, 100)))
        empty_map.append(row) 
    return empty_map

def draw_map(map, width, height, png=False):
    canvas = pygame.Surface((width*TILE_SIZE_W, height*TILE_SIZE_H))
    canvas.set_colorkey((0, 0, 0))
    for row in range(height):
        for column in range(width):
            if map[row][column][0]%2 == 0 and not png:
                color = (255, 255, 255)
            elif map[row][column][0]%2 != 0:
                    color = map[row][column][1] #randomly assigned piece color
            else:
                color = (0, 0, 0) #transparent because of colorkey
            pygame.draw.rect(canvas, color, (column * TILE_SIZE_W, row * TILE_SIZE_H, TILE_SIZE_W-1, TILE_SIZE_H-1))
    return canvas

def update_click(override=False):
    x, y = pygame.mouse.get_pos()
    if x >= GAME_SCREEN_WIDTH+TILE_SIZE_W and x < SCREEN_WIDTH-TILE_SIZE_W and y >= 100 and y < 600: 
        column = int(x/TILE_SIZE_W)-9
        row = int(y/TILE_SIZE_H)-1
        if not override:
            input_map[row][column] = (input_map[row][column][0]+1, input_map[row][column][1])
        else:
            input_map[row][column] = (1, input_map[row][column][1])

def combo_clear(map, SIZE, clear_value, sizing=False):
    clear_list = []
    max_width = 0
    min_width = 100
    for row_num, row in enumerate(map):
        filling = 0
        for column_num, (column_value, color) in enumerate(row):
            if column_value%2 != clear_value:
                filling += 1
                max_width = max(max_width, column_num)
                min_width = min(min_width, column_num)
        if filling == SIZE:
            for column_num, (column, color) in enumerate(row):
                clear_list.append((row_num, column_num)) 
    width = max_width-min_width+1

    #this is a bit more complicated cause the column values are all in seperate lists :(
    max_height = 0
    min_height = 100
    column_fillings = []
    for i in range(SIZE):
        column_fillings.append(0)

    for row_num, row in enumerate(map):
        for column_num, (column_value, color) in enumerate(map[row_num]):
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
    pygame.draw.rect(window, (0,0, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) 
    window.blit(draw_map(game_map, GAME_MAP_SIZE, GAME_MAP_SIZE), (0, 0))
    window.blit(draw_map(input_map, INPUT_MAP_SIZE, INPUT_MAP_SIZE), (900, 100))
    pygame.draw.rect(window, (0, 100, 0), (SCREEN_WIDTH-30, 0, 30, len(memory)*SCREEN_HEIGHT/3))
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

def place_piece(piece_map, piece_x, piece_y, place=True):
    placement = []
    for row_num, row in enumerate(piece_map):
        for column_num, column in enumerate(piece_map[row_num]):
            if piece_map[row_num][column_num][0]%2 == 1:
                target_row = row_num+int(piece_y)
                target_column = column_num+int(piece_x)
                if game_map[target_row][target_column][0]%2 != 1:
                    placement.append((target_row, target_column))
                else:
                    return False
    if place:
        piece_color = (random.randint(0,200), random.randint(0, 200), random.randint(0, 200))
        for row, column in placement:
            game_map[row][column] = (1, piece_color)
    return True


def generate_positions(map, piece_data):
    piece_map, piece_w, piece_h = piece_data
    open_pos = []

    for piece_y in range(GAME_MAP_SIZE-piece_h+1):
        for piece_x in range(GAME_MAP_SIZE-piece_w+1):
            if place_piece(piece_map, piece_x, piece_y, place=False):
                open_pos.append((piece_map, piece_x, piece_y))
                
    return open_pos

def algorithm(i):
    if i == 6:
        print("\n\nGame Crashed :( No solution found\n\n")
        sys.exit()       

    global game_map
    ordered_memory = list(permutations((memory)))[i]
    map_pos_0 = copy.deepcopy(game_map)
    solution = None

    '''
    The if  place piece statments are completely unnessecary, but if it ain't broke, don't fix
    This code is a uncondensed backup
    '''

    for pos1data in generate_positions(game_map, ordered_memory[0]):

        if place_piece(*pos1data):
            update_map()
            map_pos_1 = copy.deepcopy(game_map) 

            for pos2data in generate_positions(game_map, ordered_memory[1]):
                if place_piece(*pos2data):
                    update_map()

                    for pos3data in generate_positions(game_map, ordered_memory[2]):
                        if place_piece(*pos3data):
                            update_map()
                            solution = [pos1data, pos2data, pos3data]
                            break

                    if solution:
                        break
                    game_map = copy.deepcopy(map_pos_1) #if no pos3 found reset to pos 1

            if solution:
                    break
            game_map = copy.deepcopy(map_pos_0) #if no pos 2 found reset to pos 0

    if solution == None:
        algorithm(i+1)


def update_map(delay=0.05):
    render()
    time.sleep(delay)
    clear_list = combo_clear(game_map, GAME_MAP_SIZE, 0)
    if clear_list:
        for row, column in clear_list:
            game_map[row][column] = (0, (0, 0, 0))
        render()
        time.sleep(delay)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
memory = []

game_map = blank_map(GAME_MAP_SIZE)
input_map = blank_map(INPUT_MAP_SIZE)
running = True
last_time = time.time()
mouse_down = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True
            click_time = time.time()
            update_click()
            
    if mouse_down and (time.time()-click_time > 0.1):
        update_click(override=True)   
        
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not last_keys[pygame.K_SPACE]:
            piece_map, piece_w, piece_h = generate_piece()
            memory.append((piece_map, piece_w, piece_h))
            input_map = blank_map(INPUT_MAP_SIZE)
                    
    render()
    last_keys = keys
    
    if len(memory) == 3:
        algorithm(0)
        memory = []
        
