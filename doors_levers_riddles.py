import random

def place_locked_doors(grid, num_doors=2):
    dungeon_w, dungeon_h = len(grid[0]), len(grid)
    doors = []
    for _ in range(num_doors):
        while True:
            x, y = random.randint(1, dungeon_w-2), random.randint(1, dungeon_h-2)
            if grid[y][x] == 1:  # Place doors on walls
                doors.append({'pos': (x, y), 'locked': True, 'riddle': 'Solve this riddle to unlock.'})
                break
    return doors

def place_levers(grid, num_levers=2):
    dungeon_w, dungeon_h = len(grid[0]), len(grid)
    levers = []
    for _ in range(num_levers):
        while True:
            x, y = random.randint(1, dungeon_w-2), random.randint(1, dungeon_h-2)
            if grid[y][x] == 0:  # Place levers only on floor
                levers.append({'pos': (x, y), 'activated': False, 'door_idx': random.randint(0, num_levers-1)})
                break
    return levers

def use_lever(player_pos, levers, doors):
    for lever in levers:
        if lever['pos'] == tuple(player_pos) and not lever['activated']:
            lever['activated'] = True
            # Unlock corresponding door
            doors[lever['door_idx']]['locked'] = False
            return True
    return False