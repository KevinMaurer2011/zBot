import pygame
import sys
import os
import pygame_gui

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 22
CELL_SIZE = 30
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
SIDEBAR_WIDTH = 200

# Initialize pygame_gui
manager = pygame_gui.UIManager((SCREEN_SIZE + SIDEBAR_WIDTH, SCREEN_SIZE))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_SIZE + SIDEBAR_WIDTH, SCREEN_SIZE))
pygame.display.set_caption("City Grid")

# Load images
image_folder = "opt-buildings"  # Change this to your opt-buildings folder path
images = {}
for filename in os.listdir(image_folder):
    if filename.endswith((".png", ".jpg", ".bmp")):
        img = pygame.image.load(os.path.join(image_folder, filename))
        # Scale the image while maintaining aspect ratio
        img_aspect = img.get_width() / img.get_height()
        if img_aspect > 1:
            new_width = CELL_SIZE
            new_height = int(CELL_SIZE / img_aspect)
        else:
            new_width = int(CELL_SIZE * img_aspect)
            new_height = CELL_SIZE
        img = pygame.transform.scale(img, (new_width, new_height))
        # Create a new surface with alpha channel
        scaled_img = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        # Center the scaled image on the new surface
        x_offset = (CELL_SIZE - new_width) // 2
        y_offset = (CELL_SIZE - new_height) // 2
        scaled_img.blit(img, (x_offset, y_offset))
        images[filename] = scaled_img

# Mapping of two-digit codes to image filenames
code_to_image = {
    "33": "forest.jpg",
    "34": "clay.jpg",
    "35": "iron.jpg",
    "36": "lake.jpg",
    # Add more mappings as needed
}

# City grid
city_grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Selected image
selected_image = None


def parse_sharestring(sharestring):
    # Remove the first two characters (LL or WW) and any newlines
    sharestring = sharestring[2:].replace("\n", "")

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            # Skip the center 4 squares
            if (x in [10, 11]) and (y in [10, 11]):
                continue
            index = x * GRID_SIZE * 2 + y * 2
            code = sharestring[index : index + 2]
            if code in code_to_image and code_to_image[code] in images:
                city_grid[x][y] = images[code_to_image[code]]


def draw_grid():
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_SIZE, y))


def draw_city():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            # Draw the outer walls
            if x == 0 or x == GRID_SIZE - 1 or y == 0 or y == GRID_SIZE - 1:
                pygame.draw.rect(
                    screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
            # Draw the center 4 squares as red
            elif (x in [10, 11]) and (y in [10, 11]):
                pygame.draw.rect(
                    screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )
            elif city_grid[x][y]:
                screen.blit(city_grid[x][y], (x * CELL_SIZE, y * CELL_SIZE))


def draw_sidebar():
    pygame.draw.rect(screen, WHITE, (SCREEN_SIZE, 0, SIDEBAR_WIDTH, SCREEN_SIZE))
    y = 10
    x = SCREEN_SIZE + 10
    for filename, img in images.items():
        screen.blit(img, (x, y))
        y += CELL_SIZE + 5
        if y > SCREEN_SIZE - 100:  # Leave space for the input and button
            y = 10
            x += CELL_SIZE + 5


# Create text input for sharestring
sharestring_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(
        (SCREEN_SIZE, SCREEN_SIZE - 60), (SIDEBAR_WIDTH - 10, 30)
    ),
    manager=manager,
)

# Create update button
update_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        (SCREEN_SIZE, SCREEN_SIZE - 30), (SIDEBAR_WIDTH - 10, 30)
    ),
    text="Update City",
    manager=manager,
)

# Example sharestring (you can replace this with user input later)
sharestring = "LL00000000000000000000000000000000000000000000003333330000000000000000000000000000343434000000000000000000000000000000000000000035000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000034353536000000000000000000000000000000000000350000350000000000000000000000000000000000003400003400000000000000000000000000000000000033363633000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000343434000036363600000000000000000000000000003535350000000000000000000000000000000000000000000000"
# Parse the sharestring and populate the city grid
parse_sharestring(sharestring)

# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if x < SCREEN_SIZE:
                grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                if (
                    selected_image
                    and 0 < grid_x < GRID_SIZE - 1
                    and 0 < grid_y < GRID_SIZE - 1
                ):
                    if grid_x not in [10, 11] or grid_y not in [
                        10,
                        11,
                    ]:  # Avoid center 4 squares
                        city_grid[grid_x][grid_y] = selected_image
            else:
                # Check if clicked on an image in the sidebar
                sidebar_x = (x - SCREEN_SIZE) // (CELL_SIZE + 5)
                sidebar_y = y // (CELL_SIZE + 5)
                index = sidebar_y + sidebar_x * ((SCREEN_SIZE - 100) // (CELL_SIZE + 5))
                if index < len(images):
                    selected_image = list(images.values())[index]

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == update_button:
                    new_sharestring = sharestring_input.get_text()
                    if new_sharestring.startswith("LL") or new_sharestring.startswith(
                        "WW"
                    ):
                        # Clear the current city grid
                        city_grid = [
                            [None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)
                        ]
                        # Parse the new sharestring and update the city layout
                        parse_sharestring(new_sharestring)

        manager.process_events(event)

    manager.update(time_delta)

    screen.fill(WHITE)
    draw_grid()
    draw_city()
    draw_sidebar()
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
