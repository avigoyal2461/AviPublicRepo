import pygame
import time
# Initialize pygame
pygame.init()

# Set the window size
window_size = (400, 400)

# Create the window
screen = pygame.display.set_mode(window_size)

# Set the background color
screen.fill((255, 255, 255))

# Set the ball and paddle colors
ball_color = (0, 0, 0)
paddle_color = (0, 0, 0)

# Set the ball and paddle sizes
ball_size = 10
paddle_width = 10
paddle_height = 50

# Set the ball and paddle positions
ball_x = 200
ball_y = 200
paddle_x = 10
paddle_y = 175

# Set the ball and paddle speeds
ball_speed_x = 5
ball_speed_y = 5
paddle_speed = 5

# Set the game variables
score = 0
game_over = False

# Set the font for the score
font = pygame.font.Font(None, 36)

# Create the speed slider
slider = pygame.Rect(10, 10, 200, 20)

time.sleep(1239)

# Run the game loop
while not game_over:
    quit()
# try_one()
  # Handle events
# def try_one():
# # Initialize pygame
#     pygame.init()

#     # Set the window size
#     window_size = (400, 400)

#     # Create the window
#     screen = pygame.display.set_mode(window_size)

#     # Set the background color
#     screen.fill((255, 255, 255))

#     # Set the circle color
#     color = (0, 0, 255)  # blue

#     # Set the circle radius
#     radius = 50

#     # Set the circle position
#     x = 200
#     y = 200

#     # Draw the circle
#     pygame.draw.circle(screen, color, (x, y), radius)

#     # Update the display
#     pygame.display.flip()

#     # Run the game loop
#     running = True
#     while running:
#       for event in pygame.event.get():
#           if event.type == pygame.QUIT:
#             running = False

#     # Quit pygame
#     pygame.quit()