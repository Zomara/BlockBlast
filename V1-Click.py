import pygame, time, random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
MAP_SIZE = 8
TILE_SIZE_W = int(SCREEN_WIDTH / MAP_SIZE)
TILE_SIZE_H = int(SCREEN_HEIGHT / MAP_SIZE)
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def blank_map():
    map = []
    for i in range(MAP_SIZE):
        row = []
        for j in range(MAP_SIZE):
            row.append(0)
        map.append(row)
    return map

def draw_map(map):
    for row in range(MAP_SIZE):
        for column in range(MAP_SIZE):
            if map[row][column]%2 == 0:
                color = (0, 40, 75)
            else:
                color = (0, 0, 50)
            pygame.draw.rect(window, color, (column * TILE_SIZE_W, row * TILE_SIZE_H, TILE_SIZE_W-1, TILE_SIZE_H-1))

def update_click(map):
    x, y = pygame.mouse.get_pos()
    column = int(x/TILE_SIZE_W)
    row = int(y/TILE_SIZE_H)
    map[row][column] += 1


def combo_clear(map):
    reset_list = []

    for row_num, row in enumerate(map):
        filling = 0
        for column_value in row:
            if column_value%2 != 0:
                filling += 1
        if filling == MAP_SIZE:
            for column_num, column in enumerate(row):
                reset_list.append((row_num, column_num))

    #this is a bit more complicated cause the column values are all in seperate lists :(
    column_fillings = []
    for i in range(MAP_SIZE):
        column_fillings.append(0)

    for row_num, row in enumerate(map):
        for column_num, column_value in enumerate(map[row_num]):
            if column_value%2 != 0:
                column_fillings[column_num] += 1

    for column_num, filling in enumerate(column_fillings):
        if filling == MAP_SIZE:
            for row_num, row in enumerate(map):
                reset_list.append((row_num, column_num))


    reset_list = list(dict.fromkeys(reset_list))
    for row_num, column_num in reset_list:
        map[row_num][column_num] += 1
    
            
def render(map):
    draw_map(map)
    pygame.display.update()

running = True
map = blank_map()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            update_click(map)

    combo_clear(map)
    render(map)
