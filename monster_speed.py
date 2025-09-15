MONSTER_MOVE_INTERVAL = 12  # Move every 12 frames instead of every frame

# In your main loop:
monster_move_counter = 0
while running:
    # ... your event loop ...
    monster_move_counter += 1
    if monster_move_counter >= MONSTER_MOVE_INTERVAL:
        for m in monsters:
            # monster move logic here
            pass
        monster_move_counter = 0