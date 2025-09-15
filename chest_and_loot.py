import random

# Define chest loot types
LOOT_TYPES = ['key', 'gothic_relic']

def place_chests(grid, num_chests=4):
    dungeon_w, dungeon_h = len(grid[0]), len(grid)
    chests = []
    for _ in range(num_chests):
        while True:
            x, y = random.randint(1, dungeon_w-2), random.randint(1, dungeon_h-2)
            if grid[y][x] == 0:   # Place only on floor, not walls
                loot = random.choice(LOOT_TYPES)
                chests.append({'pos': (x, y), 'loot': loot, 'opened': False})
                break
    return chests

def open_chest(player_pos, chests):
    for chest in chests:
        if chest['pos'] == tuple(player_pos) and not chest['opened']:
            chest['opened'] = True
            return chest['loot']
    return None