import random

map_key = {
    0: "Empty",
    1: "Spike",
    2: "Cube",
}

def generate_map(rows=6, cols=40, spike_chance=0.15, cube_chance=0.2, min_spike_gap=2):
    """
    Generate a playable map.

    rows: number of rows (6 recommended)
    cols: number of columns (map width)
    spike_chance: probability a spike appears in bottom row
    cube_chance: probability a cube platform appears in middle rows
    min_spike_gap: minimum empty spaces between spikes
    """
    game_map = []

    # Top rows (mostly empty)
    for r in range(rows-2):
        row = [0]*cols
        # Randomly add some cube platforms
        for c in range(cols):
            if random.random() < cube_chance:
                row[c] = 2
        game_map.append(row)

    # Second to last row (can have cubes)
    row = [0]*cols
    for c in range(cols):
        if random.random() < cube_chance:
            row[c] = 2
    game_map.append(row)

    # Bottom row (spikes with safe spacing)
    bottom_row = [0]*cols
    c = 0
    while c < cols:
        if random.random() < spike_chance:
            bottom_row[c] = 1
            c += min_spike_gap  # leave safe gap after spike
        else:
            c += 1
    game_map.append(bottom_row)

    return game_map

# Example usage
test = [

    # Row 0 (highest)
    [0]*80,

    # Row 1
    [0]*80,

    # Row 2
    [0]*80,

    # Row 3 (platforms)
    [
        0,0,0,2,2,2,0,0,0,0,0,0,  2,2,0,0,0,0,0,0,  2,2,2,0,0,0,0,0,
        0,2,0,0,0,2,2,2,0,0,0,  2,2,0,0,0,0,  2,2,2,0,0,0,0,
        0,2,2,0,0,0,0,  2,2,2,0,0,0,0,0,
        2,2,0,0,0,0,  2,2,2,0,0,0,0,  0,2,2,2,0,0,0,
        0,0,2,2,0,0,0,  2,2,2,0,0,0
    ],

    # Row 4
    [0]*80,

    # Row 5 (spikes — spaced for playability)
    [
        0,1,0,0,0,0,1,0,0,0,0,0,  1,0,0,0,0,1,0,0,0,0,
        1,0,0,0,0,1,0,0,0,0,  1,0,0,0,0,1,0,0,0,
        0,1,0,0,0,0,0,1,0,0,0,0,
        1,0,0,0,0,0,1,0,0,0,0,
        1,0,0,0,0,0,1,0,0,0,0,
        0,1,0,0,0,0,0,1,0,0,0,
        0,1,0,0,0,0,0,1,0,0,0,0,
        1,0,0,0,0,0,1,0,0,0
    ]
]