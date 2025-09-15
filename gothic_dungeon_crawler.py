import pygame
import random
import os

# --- Settings ---
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
TILE_SIZE = 32
FPS = 60

# Colors
BLACK = (20, 18, 23)
GRAY = (64, 60, 70)
RED = (120, 10, 30)
TORCH_YELLOW = (220, 180, 60)
PLAYER_COLOR = (200, 200, 255)
WALL_COLOR = (60, 50, 70)
FLOOR_COLOR = (35, 30, 40)
CHEST_COLOR = (120, 90, 40)
DOOR_COLOR = (40, 30, 20)
LEVER_COLOR = (200, 150, 80)

# --- Asset Loading Helpers ---

pygame.init()
pygame.mixer.init() # bug in pygame

# Sound effect (recommended .wav or .ogg, .mp3 sometimes fails)
sound_path = 'asset/sfx/sword_attack.wav'
try:
    sword_sound = pygame.mixer.Sound(sound_path)
    sword_sound.play()
except Exception as e:
    print("Error playing sword sound:", e)

# Music (recommended .mp3, .ogg)
music_path = 'asset/music/gothic-candlelight-gothic-mystery-soundtrack-1987.mp3'
try:
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Loop
except Exception as e:
    print("Error playing music:", e)

def load_image(name):
    # Assumes asset PNGs converted from SVG exist
    fullname = os.path.join('asset', name)
    image = pygame.image.load(fullname)
    return image

# --- Dungeon Generator ---
def generate_dungeon(w, h):
    grid = [[1 if x==0 or y==0 or x==w-1 or y==h-1 else 0 for x in range(w)] for y in range(h)]
    # Add some random walls
    for _ in range(w*h//5):
        wx, wy = random.randint(1, w-2), random.randint(1, h-2)
        grid[wy][wx] = 1
    # Add torches
    torches = [(random.randint(1,w-2), random.randint(1,h-2)) for _ in range(6)]
    return grid, torches

# --- Chest, Loot System ---
LOOT_TYPES = ['key', 'gothic_relic']
def place_chests(grid, num_chests=4):
    dungeon_w, dungeon_h = len(grid[0]), len(grid)
    chests = []
    for _ in range(num_chests):
        while True:
            x, y = random.randint(1, dungeon_w-2), random.randint(1, dungeon_h-2)
            # Place only on floor, not walls
            if grid[y][x] == 0:
                loot = random.choice(LOOT_TYPES)
                chests.append({'pos': (x, y), 'loot': loot, 'opened': False})
                break
    return chests

# --- Locked Doors & Levers ---
def place_locked_doors(grid, num_doors=2):
    dungeon_w, dungeon_h = len(grid[0]), len(grid)
    doors = []
    for _ in range(num_doors):
        while True:
            x, y = random.randint(1, dungeon_w-2), random.randint(1, dungeon_h-2)
            if grid[y][x] == 1:  # Place doors on walls
                doors.append({'pos': (x, y), 'locked': True, 'riddle': 'What walks on four legs in the morning, two legs at noon, and three in the evening?'})
                break
    return doors

def place_levers(grid, num_levers=2):
    dungeon_w, dungeon_h = len(grid[0]), len(grid)
    levers = []
    for idx in range(num_levers):
        while True:
            x, y = random.randint(1, dungeon_w-2), random.randint(1, dungeon_h-2)
            if grid[y][x] == 0:  # Place levers only on floor
                levers.append({'pos': (x, y), 'activated': False, 'door_idx': idx})
                break
    return levers

# --- Monster System ---
MONSTER_TYPES = ['vampire', 'skeleton', 'ghost']
def place_monsters(grid, num_monsters=4):
    dungeon_w, dungeon_h = len(grid[0]), len(grid)
    monsters = []
    for _ in range(num_monsters):
        while True:
            x, y = random.randint(2, dungeon_w-3), random.randint(2, dungeon_h-3)
            if grid[y][x] == 0:
                mtype = random.choice(MONSTER_TYPES)
                monsters.append({'pos': [x, y], 'type': mtype})
                break
    return monsters

# --- Tutorial System ---
TUTORIAL_STEPS = [
    "Use arrow keys to move.",
    "Walk to a chest (brown) and press SPACE to open.",
    "Pick up a key or relic from a chest.",
    "Find a locked door (dark) and press SPACE to unlock if you have a key.",
    "Look for levers (gold) and press SPACE to activate.",
    "Avoid monsters! If you touch one, you die.",
    "Solve riddles when prompted at doors.",
    "Good luck exploring the gothic dungeon!",
]

# --- Main Game ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Times New Roman", 18)

    # Load assets
    images = {
        'player': load_image('player_knight.png'),
        'vampire': load_image('vampire.png'),
        'skeleton': load_image('skeleton.png'),
        'ghost': load_image('ghost.png'),
        'torch': load_image('torch.png'),
        'chest': load_image('chest.png'),
        'door': load_image('door.png'),
        'lever': load_image('lever.png'),
    }

    dungeon_w, dungeon_h = SCREEN_WIDTH//TILE_SIZE, SCREEN_HEIGHT//TILE_SIZE
    grid, torches = generate_dungeon(dungeon_w, dungeon_h)
    player_pos = [2, 2]
    monsters = place_monsters(grid)
    chests = place_chests(grid)
    doors = place_locked_doors(grid)
    levers = place_levers(grid)
    inventory = {'key': 0, 'gothic_relic': 0}
    tutorial_idx = 0

    monster_move_counter = 0
    MONSTER_MOVE_INTERVAL = 15

    running = True
    show_riddle = False
    riddle_door_idx = None
    riddle_answer = ""
    message = ""

    while running:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_UP: dy = -1
                if event.key == pygame.K_DOWN: dy = 1
                if event.key == pygame.K_LEFT: dx = -1
                if event.key == pygame.K_RIGHT: dx = 1
                # Move player
                if dx != 0 or dy != 0:
                    nx, ny = player_pos[0]+dx, player_pos[1]+dy
                    if 0 <= nx < dungeon_w and 0 <= ny < dungeon_h and grid[ny][nx] == 0:
                        player_pos = [nx, ny]
                        if tutorial_idx < len(TUTORIAL_STEPS) and tutorial_idx == 0:
                            tutorial_idx += 1
                # Interact (SPACE)
                elif event.key == pygame.K_SPACE:
                    # Chest
                    for chest in chests:
                        if chest['pos'] == tuple(player_pos) and not chest['opened']:
                            chest['opened'] = True
                            loot = chest['loot']
                            inventory[loot] += 1
                            message = f"You found a {loot}!"
                            if tutorial_idx < len(TUTORIAL_STEPS) and tutorial_idx == 1:
                                tutorial_idx += 1
                            break
                    # Door
                    for idx, door in enumerate(doors):
                        if door['pos'] == tuple(player_pos):
                            if door['locked']:
                                if inventory['key'] > 0:
                                    show_riddle = True
                                    riddle_door_idx = idx
                                    message = "A riddle blocks your way. Answer it!"
                                    if tutorial_idx < len(TUTORIAL_STEPS) and tutorial_idx == 3:
                                        tutorial_idx += 1
                                else:
                                    message = "The door is locked. You need a key."
                            else:
                                message = "The door is open!"
                            break
                    # Lever
                    for lever in levers:
                        if lever['pos'] == tuple(player_pos) and not lever['activated']:
                            lever['activated'] = True
                            doors[lever['door_idx']]['locked'] = False
                            message = "You hear a door unlock in the distance."
                            if tutorial_idx < len(TUTORIAL_STEPS) and tutorial_idx == 4:
                                tutorial_idx += 1
                            break
                # Riddle input
                elif show_riddle and event.unicode.isalpha():
                    riddle_answer += event.unicode
                elif show_riddle and event.key == pygame.K_RETURN:
                    if riddle_answer.lower().strip() == "man":
                        doors[riddle_door_idx]['locked'] = False
                        inventory['key'] -= 1
                        message = "You solved the riddle! The door unlocks."
                        show_riddle = False
                        riddle_answer = ""
                        if tutorial_idx < len(TUTORIAL_STEPS) and tutorial_idx == 6:
                            tutorial_idx += 1
                    else:
                        message = "Wrong answer. Try again."
                        riddle_answer = ""

        # --- Monster movement ---
        monster_move_counter += 1
        if monster_move_counter >= MONSTER_MOVE_INTERVAL:
            for m in monsters:
                mdx, mdy = random.choice([(0,1),(0,-1),(1,0),(-1,0),(0,0)])
                nx, ny = m['pos'][0]+mdx, m['pos'][1]+mdy
                if 0 <= nx < dungeon_w and 0 <= ny < dungeon_h and grid[ny][nx] == 0:
                    m['pos'][0], m['pos'][1] = nx, ny
            monster_move_counter = 0

        # --- Check collisions ---
        for m in monsters:
            if tuple(m['pos']) == tuple(player_pos):
                message = f"You were slain by a {m['type']}! Game Over."
                running = False

        # --- Draw ---
        screen.fill(BLACK)
        # Dungeon tiles
        for y in range(dungeon_h):
            for x in range(dungeon_w):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if grid[y][x]==1:
                    pygame.draw.rect(screen, WALL_COLOR, rect)
                else:
                    pygame.draw.rect(screen, FLOOR_COLOR, rect)
        # Torches
        for tx, ty in torches:
            screen.blit(images['torch'], (tx*TILE_SIZE, ty*TILE_SIZE))
        # Chests
        for chest in chests:
            if not chest['opened']:
                screen.blit(images['chest'], (chest['pos'][0]*TILE_SIZE, chest['pos'][1]*TILE_SIZE))
        # Doors
        for door in doors:
            screen.blit(images['door'], (door['pos'][0]*TILE_SIZE, door['pos'][1]*TILE_SIZE))
        # Levers
        for lever in levers:
            if not lever['activated']:
                screen.blit(images['lever'], (lever['pos'][0]*TILE_SIZE, lever['pos'][1]*TILE_SIZE))
        # Player
        screen.blit(images['player'], (player_pos[0]*TILE_SIZE, player_pos[1]*TILE_SIZE))
        # Monsters
        for m in monsters:
            screen.blit(images[m['type']], (m['pos'][0]*TILE_SIZE, m['pos'][1]*TILE_SIZE))
        
        # --- Tutorial UI ---
        if tutorial_idx < len(TUTORIAL_STEPS):
            tut_text = font.render("Tutorial: "+TUTORIAL_STEPS[tutorial_idx], True, (255,255,200))
            screen.blit(tut_text, (20,SCREEN_HEIGHT-40))
        # --- Message UI ---
        if message:
            msg_text = font.render(message, True, (255,200,200))
            screen.blit(msg_text, (20,SCREEN_HEIGHT-60))
        # --- Riddle UI ---
        if show_riddle:
            riddle = doors[riddle_door_idx]['riddle']
            riddle_text = font.render("Riddle: " + riddle, True, (255,255,220))
            answer_text = font.render("Your answer: " + riddle_answer, True, (255,255,220))
            screen.blit(riddle_text, (20, 20))
            screen.blit(answer_text, (20, 40))

        # --- Inventory UI ---
        inv_text = font.render(f"Keys: {inventory['key']} | Relics: {inventory['gothic_relic']}", True, (200,255,200))
        screen.blit(inv_text, (20,10))

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()